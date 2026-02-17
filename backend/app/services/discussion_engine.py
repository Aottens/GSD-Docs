"""Discussion engine service for orchestrating discussion workflow.

Implements the v1.0 pattern: the backend drives the conversation with
small, scoped LLM calls per step (one question, one intro). The state
machine controls flow; the LLM generates content.
"""

import json
import logging
import re
from typing import AsyncGenerator, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import Settings
from app.llm.provider import LLMProvider
from app.models.conversation import Conversation, Message, ConversationStatus, MessageRole, MessageType
from app.models.project import Project
from app.prompts.discuss_phase import (
    detect_content_types,
    get_gray_areas,
    build_system_prompt,
    PROJECT_TYPE_PHASES,
    GRAY_AREA_PATTERNS,
    GENERATE_QUESTION_PROMPT,
    GENERATE_FOUNDATION_QUESTION_PROMPT,
    GENERATE_TOPIC_INTRO_PROMPT,
)
from app.services.conversation_state import ConversationState, ConversationPhase, detect_foundation_phase
from app.services.decision_extractor import extract_verbatim_decision, is_meta_message

logger = logging.getLogger(__name__)


class DiscussionEngine:
    """
    Orchestrates discussion workflow using v1.0 patterns.

    The state machine drives conversation flow. Each turn makes at most
    one small, scoped LLM call (for a question or topic intro). Check-ins
    and completion cards are pure Python — no LLM needed.
    """

    def __init__(self, db: AsyncSession, llm: LLMProvider, settings: Settings):
        self.db = db
        self.llm = llm
        self.settings = settings

    # ── start_discussion (unchanged from Plans 01-05) ───────────────

    async def start_discussion(self, project_id: int, phase_number: int) -> Conversation:
        """
        Start a new discussion for a phase.

        Steps:
        1. Load project from DB (get type, language)
        2. Parse ROADMAP.md to get phase goal
        3. Detect content types from phase goal
        4. Detect if Foundation phase
        5. Initialize ConversationState
        6. If Foundation: skip topic selection, create intake greeting
        7. If NOT Foundation: create topic selection card
        8. Build system prompt and create conversation
        """
        project_data = await self._load_project(project_id)
        project_type = project_data.get("type", "B")
        project_language = project_data.get("language", "nl")

        phase_info = self._parse_roadmap_for_phase(project_type, phase_number)
        phase_goal = phase_info["goal"]
        phase_name = phase_info["name"]

        is_foundation = detect_foundation_phase(phase_number, phase_goal)
        content_types = detect_content_types(phase_goal)
        gray_areas = [] if is_foundation else get_gray_areas(content_types)

        baseline_summary = None
        if project_type in ["C", "D"]:
            baseline_summary = self._load_baseline_summary(project_id)

        system_prompt = build_system_prompt(
            phase_goal=phase_goal,
            phase_number=phase_number,
            phase_name=phase_name,
            content_types=content_types,
            project_type=project_type,
            project_language=project_language,
            gray_areas=gray_areas,
            baseline_summary=baseline_summary,
        )

        state = ConversationState(is_foundation=is_foundation)
        if is_foundation:
            state.phase = ConversationPhase.discussion
            state.current_topic = "Foundation"
        else:
            state.phase = ConversationPhase.topic_selection

        conversation = Conversation(
            project_id=project_id,
            phase_number=phase_number,
            status=ConversationStatus.active.value,
            title=f"Phase {phase_number}: {phase_name}",
            summary_data={
                "phase_number": phase_number,
                "phase_name": phase_name,
                "phase_goal": phase_goal,
                "content_types": content_types,
                "gray_areas": [area["topic"] for area in gray_areas],
                **state.to_summary_data(),
            },
        )
        self.db.add(conversation)
        await self.db.flush()

        # System message
        system_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.system.value,
            content=system_prompt,
            message_type=MessageType.text.value,
        )
        self.db.add(system_message)

        # Initial assistant message
        if is_foundation:
            if project_language == "nl":
                greeting = (
                    f"Welkom bij de Foundation bespreking voor dit {project_type} project! "
                    "Laten we beginnen met het vastleggen van de basis informatie over het systeem en de scope."
                )
            else:
                greeting = (
                    f"Welcome to the Foundation discussion for this Type {project_type} project! "
                    "Let's start by capturing the fundamental information about the system and scope."
                )

            assistant_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.assistant.value,
                content=greeting,
                message_type=MessageType.text.value,
            )
        else:
            topic_selection_text = self._build_topic_selection_message(
                phase_name, gray_areas, project_language
            )
            assistant_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.assistant.value,
                content=topic_selection_text,
                message_type=MessageType.topic_selection.value,
                metadata_json={
                    "topics": [
                        {
                            "id": f"topic_{i}",
                            "name": area["topic"],
                            "description": area["description"],
                        }
                        for i, area in enumerate(gray_areas)
                    ],
                    "include_discretion_option": True,
                },
            )

        self.db.add(assistant_message)
        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    # ── send_message (REWRITTEN — scoped LLM calls) ────────────────

    async def send_message(
        self,
        conversation_id: int,
        content: str,
        attachments: Optional[list[str]] = None,
    ) -> AsyncGenerator[dict, None]:
        """
        Process user message and generate response with state-aware orchestration.

        Instead of one big LLM call with full history and XML parsing, each
        phase makes at most one small, scoped LLM call. Check-ins and
        completion cards are pure Python.

        Yields:
            SSE event dicts: message_delta, message_complete, question_card,
            decision_captured, topic_boundary, check_in, completion_card, done
        """
        # Step 1: Load conversation + state
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one()
        state = ConversationState.from_summary_data(conversation.summary_data)

        # Load project data for language/phase info
        project_data = await self._load_project(conversation.project_id)
        language = project_data.get("language", "nl")

        # Step 2: Persist user message
        user_message = Message(
            conversation_id=conversation_id,
            role=MessageRole.user.value,
            content=content,
            message_type=MessageType.text.value,
            metadata_json={"attachments": attachments} if attachments else None,
        )
        self.db.add(user_message)
        await self.db.commit()

        # Step 3+4: Process phase transitions + generate response
        try:
            if state.phase == ConversationPhase.topic_selection:
                async for event in self._handle_topic_selection(state, conversation, content, language):
                    yield event

            elif state.phase == ConversationPhase.discussion:
                async for event in self._handle_discussion(state, conversation, content, language):
                    yield event

            elif state.phase == ConversationPhase.check_in:
                async for event in self._handle_check_in(state, conversation, content, language):
                    yield event

            elif state.phase == ConversationPhase.completion:
                async for event in self._handle_completion(state, conversation, content, language):
                    yield event

            # Step 6: Update state + commit
            conversation.summary_data.update(state.to_summary_data())
            conversation.updated_at = datetime.utcnow()
            await self.db.commit()

            # Step 7: Done
            yield {"event": "done", "data": {}}

        except Exception as e:
            logger.exception("Error in send_message")
            yield {"event": "error", "data": {"error": str(e)}}
            raise

    # ── Phase handlers ──────────────────────────────────────────────

    async def _handle_topic_selection(
        self, state: ConversationState, conversation: Conversation, content: str, language: str
    ) -> AsyncGenerator[dict, None]:
        """Handle topic_selection phase: parse selection, start first topic."""
        selected_topics, discretion_topics = self._parse_topic_selection(
            content, conversation.summary_data.get("gray_areas", [])
        )
        state.confirm_topics(selected_topics, discretion_topics)

        first_topic = state.next_topic()
        if first_topic:
            state.start_topic(first_topic)

            # Emit topic_boundary(starting)
            yield {
                "event": "topic_boundary",
                "data": {"topic_boundary": {"topic": first_topic, "status": "starting"}}
            }
            await self._persist_message(
                conversation.id, MessageType.topic_boundary,
                f"Starting topic: {first_topic}",
                {"topic_boundary": {"topic": first_topic, "status": "starting"}},
            )

            # Generate topic intro
            intro = await self._generate_topic_intro(
                first_topic,
                self._get_topic_description(first_topic, conversation.summary_data),
                language,
            )
            if intro:
                yield {"event": "message_delta", "data": {"delta": intro}}
                yield {"event": "message_complete", "data": {"final": intro}}
                await self._persist_message(conversation.id, MessageType.text, intro)

            # Generate first question
            question_data = await self._generate_question(state, conversation, language)
            yield {"event": "question_card", "data": question_data}
            await self._persist_message(
                conversation.id, MessageType.question_card,
                question_data.get("question", ""),
                question_data,
            )

    async def _handle_discussion(
        self, state: ConversationState, conversation: Conversation, content: str, language: str
    ) -> AsyncGenerator[dict, None]:
        """Handle discussion phase: extract decision, ask next question or check-in."""
        # Extract decision from user's answer (silently accumulate — no SSE event)
        if not is_meta_message(content) and state.current_topic:
            last_question = await self._get_last_question(conversation.id)
            decision = extract_verbatim_decision(content, state.current_topic, last_question)

            if decision:
                state.decisions.append(decision)

            # Foundation: track covered areas using fallback detection
            if state.is_foundation:
                area = state.detect_covered_area_with_fallback(last_question, content)
                if area and area not in state.foundation_areas_covered:
                    state.foundation_areas_covered.append(area)

        # Increment question counter, check for check-in
        checkin_result = state.increment_question()
        needs_checkin = checkin_result in ("check_in", "force_check_in")

        # Also trigger check-in when all probes for this topic are covered
        if not state.is_foundation and not needs_checkin:
            all_probes = self._get_probe_list(state.current_topic)
            if all_probes and len(state.probes_covered) >= len(all_probes):
                needs_checkin = True

        # Foundation sufficiency check
        if state.is_foundation and self._check_foundation_sufficiency(state):
            state.start_completion()
            completion_msg = self._build_completion_message(state, language)
            yield {
                "event": "completion_card",
                "data": {
                    "completion": {
                        "message": completion_msg,
                        "decisions_count": len(state.decisions),
                        "topics_covered": ["Foundation"],
                    }
                }
            }
            await self._persist_message(
                conversation.id, MessageType.completion_card, completion_msg,
                {"completion": {"message": completion_msg, "decisions_count": len(state.decisions), "topics_covered": ["Foundation"]}},
            )
            return

        if needs_checkin and not state.is_foundation:
            # Transition to check_in phase
            state.phase = ConversationPhase.check_in
            checkin_msg = self._build_checkin_message(state, language)

            # Collect topic decisions for the Beslissingen tab (shown at check-in time)
            topic_decisions = [
                d for d in state.decisions
                if isinstance(d, dict) and d.get("topic", "").lower() == (state.current_topic or "").lower()
            ]

            yield {
                "event": "check_in",
                "data": {
                    "message": checkin_msg,
                    "decisions": topic_decisions,
                    "all_decisions": state.decisions,
                }
            }
            await self._persist_message(
                conversation.id, MessageType.check_in, checkin_msg,
                {"decisions": topic_decisions, "all_decisions": state.decisions},
            )
        else:
            # Ask next question
            question_data = await self._generate_question(state, conversation, language)
            yield {"event": "question_card", "data": question_data}
            await self._persist_message(
                conversation.id, MessageType.question_card,
                question_data.get("question", ""),
                question_data,
            )

    async def _handle_check_in(
        self, state: ConversationState, conversation: Conversation, content: str, language: str
    ) -> AsyncGenerator[dict, None]:
        """Handle check_in phase: continue or move to next topic."""
        normalized = content.strip().lower()

        if "next" in normalized or "volgende" in normalized:
            # Complete current topic
            completed_topic = state.current_topic
            state.complete_topic()

            if completed_topic:
                yield {
                    "event": "topic_boundary",
                    "data": {"topic_boundary": {"topic": completed_topic, "status": "complete"}}
                }
                await self._persist_message(
                    conversation.id, MessageType.topic_boundary,
                    f"Completed topic: {completed_topic}",
                    {"topic_boundary": {"topic": completed_topic, "status": "complete"}},
                )

            next_topic = state.next_topic()
            if next_topic:
                state.start_topic(next_topic)
                yield {
                    "event": "topic_boundary",
                    "data": {"topic_boundary": {"topic": next_topic, "status": "starting"}}
                }
                await self._persist_message(
                    conversation.id, MessageType.topic_boundary,
                    f"Starting topic: {next_topic}",
                    {"topic_boundary": {"topic": next_topic, "status": "starting"}},
                )

                # Topic intro
                intro = await self._generate_topic_intro(
                    next_topic,
                    self._get_topic_description(next_topic, conversation.summary_data),
                    language,
                )
                if intro:
                    yield {"event": "message_delta", "data": {"delta": intro}}
                    yield {"event": "message_complete", "data": {"final": intro}}
                    await self._persist_message(conversation.id, MessageType.text, intro)

                # First question for new topic
                question_data = await self._generate_question(state, conversation, language)
                yield {"event": "question_card", "data": question_data}
                await self._persist_message(
                    conversation.id, MessageType.question_card,
                    question_data.get("question", ""),
                    question_data,
                )

            elif state.all_topics_complete():
                # All topics done
                state.start_completion()
                completion_msg = self._build_completion_message(state, language)
                yield {
                    "event": "completion_card",
                    "data": {
                        "completion": {
                            "message": completion_msg,
                            "decisions_count": len(state.decisions),
                            "topics_covered": state.completed_topics,
                        }
                    }
                }
                await self._persist_message(
                    conversation.id, MessageType.completion_card, completion_msg,
                    {"completion": {"message": completion_msg, "decisions_count": len(state.decisions), "topics_covered": state.completed_topics}},
                )
        else:
            # Continue with more questions on current topic
            state.phase = ConversationPhase.discussion
            state.questions_in_current_topic = 0  # Reset counter for next batch

            question_data = await self._generate_question(state, conversation, language)
            yield {"event": "question_card", "data": question_data}
            await self._persist_message(
                conversation.id, MessageType.question_card,
                question_data.get("question", ""),
                question_data,
            )

    async def _handle_completion(
        self, state: ConversationState, conversation: Conversation, content: str, language: str
    ) -> AsyncGenerator[dict, None]:
        """Handle completion phase: add more or confirm done."""
        normalized = content.strip().lower()

        if "meer" in normalized or "add more" in normalized or "more" in normalized:
            # Back to discussion with freeform topic
            state.phase = ConversationPhase.discussion
            state.current_topic = "Additional Topics"
            state.questions_in_current_topic = 0

            question_data = await self._generate_question(state, conversation, language)
            yield {"event": "question_card", "data": question_data}
            await self._persist_message(
                conversation.id, MessageType.question_card,
                question_data.get("question", ""),
                question_data,
            )

        elif "bevestig" in normalized or "confirm" in normalized:
            # Acknowledge — frontend will call preview-context endpoint
            if language == "nl":
                msg = "Discussie afgerond. U kunt nu de CONTEXT.md bekijken en bevestigen."
            else:
                msg = "Discussion complete. You can now preview and confirm the CONTEXT.md."
            yield {"event": "message_delta", "data": {"delta": msg}}
            yield {"event": "message_complete", "data": {"final": msg}}
            await self._persist_message(conversation.id, MessageType.text, msg)

    # ── Scoped LLM call helpers ─────────────────────────────────────

    async def _generate_question(
        self, state: ConversationState, conversation: Conversation, language: str
    ) -> dict:
        """
        Generate ONE question via a scoped LLM call.

        For Foundation: uses GENERATE_FOUNDATION_QUESTION_PROMPT
        For regular: uses GENERATE_QUESTION_PROMPT targeting the first uncovered probe
        """
        topic_qa = await self._get_topic_qa(conversation.id)

        if state.is_foundation:
            prompt = GENERATE_FOUNDATION_QUESTION_PROMPT.format(
                covered_areas=", ".join(state.foundation_areas_covered) if state.foundation_areas_covered else "none yet",
                topic_qa=topic_qa,
                language=language,
            )
        else:
            phase_name = conversation.summary_data.get("phase_name", "")
            phase_goal = conversation.summary_data.get("phase_goal", "")

            # Get uncovered probes only
            all_probes = self._get_probe_list(state.current_topic)
            uncovered = [
                (i, q) for i, q in enumerate(all_probes)
                if i not in state.probes_covered
            ]

            if uncovered:
                next_idx, next_probe = uncovered[0]
                remaining = [q for _, q in uncovered[1:]]
            else:
                next_probe = f"General follow-up about {state.current_topic}"
                remaining = []
                next_idx = None

            prompt = GENERATE_QUESTION_PROMPT.format(
                topic=state.current_topic or "",
                phase_name=phase_name,
                phase_goal=phase_goal,
                next_uncovered_probe=next_probe,
                remaining_uncovered_probes="\n".join(f"- {q}" for q in remaining) if remaining else "(none)",
                topic_qa=topic_qa,
                language=language,
            )

        messages = [{"role": "user", "content": prompt}]

        try:
            raw = await self.llm.complete(messages, max_tokens=256, temperature=0.5)
            result = self._parse_question_json(raw)

            # Mark the first uncovered probe as covered
            if not state.is_foundation and next_idx is not None:
                state.probes_covered.append(next_idx)

            return result
        except Exception as e:
            logger.warning("LLM question generation failed: %s", e)
            return self._fallback_question(state, language)

    async def _generate_topic_intro(
        self, topic: str, description: str, language: str
    ) -> str:
        """Generate a brief topic introduction via scoped LLM call."""
        prompt = GENERATE_TOPIC_INTRO_PROMPT.format(
            topic=topic,
            description=description or topic,
            phase_name="",
            language=language,
        )
        messages = [{"role": "user", "content": prompt}]

        try:
            return await self.llm.complete(messages, max_tokens=128, temperature=0.5)
        except Exception as e:
            logger.warning("LLM topic intro failed: %s", e)
            if language == "nl":
                return f"Laten we het hebben over: {topic}."
            return f"Let's discuss: {topic}."

    def _build_checkin_message(self, state: ConversationState, language: str) -> str:
        """Build check-in message with decision summary (v1.0 Step 5.3)."""
        topic = state.current_topic or "dit onderwerp"

        # Filter decisions for current topic
        topic_decisions = [
            d for d in state.decisions
            if isinstance(d, dict) and d.get("topic", "").lower() == (state.current_topic or "").lower()
        ]

        if topic_decisions:
            bullets = "\n".join(f"- {d.get('decision', d.get('value', str(d)))}" for d in topic_decisions)
            if language == "nl":
                return (
                    f"Vastgelegd voor {topic}:\n"
                    f"{bullets}\n\n"
                    "Nog iets voor dit onderwerp, of door naar het volgende?"
                )
            return (
                f"Captured for {topic}:\n"
                f"{bullets}\n\n"
                "Anything else for this topic, or move to the next?"
            )
        else:
            if language == "nl":
                return (
                    f"We hebben {topic} besproken.\n\n"
                    "Nog iets voor dit onderwerp, of door naar het volgende?"
                )
            return (
                f"We've discussed {topic}.\n\n"
                "Anything else for this topic, or move to the next?"
            )

    def _build_completion_message(self, state: ConversationState, language: str) -> str:
        """Build completion message. Pure Python, no LLM call."""
        if language == "nl":
            return "Alle geselecteerde onderwerpen zijn besproken."
        return "All selected topics have been discussed."

    def _check_foundation_sufficiency(self, state: ConversationState) -> bool:
        """
        Check if Foundation intake has gathered enough information.

        Pure Python heuristic:
        - After 8+ questions AND 4+ of 5 areas covered → sufficient
        - Hard cap: 12 questions → always sufficient
        """
        q_count = state.questions_in_current_topic
        areas_count = len(state.foundation_areas_covered)

        if q_count >= 12:
            return True
        if q_count >= 8 and areas_count >= 4:
            return True
        return False

    # ── DB/data helpers ─────────────────────────────────────────────

    async def _persist_message(
        self,
        conversation_id: int,
        message_type: MessageType,
        content: str,
        metadata: Optional[dict] = None,
    ) -> None:
        """Persist an assistant message with correct message_type."""
        msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.assistant.value,
            content=content,
            message_type=message_type.value,
            metadata_json=metadata,
        )
        self.db.add(msg)
        await self.db.flush()

    async def _get_topic_qa(self, conversation_id: int) -> str:
        """Get all Q&A pairs for the current topic (since last topic_boundary)."""
        # Find the most recent topic_boundary message
        boundary_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.message_type == MessageType.topic_boundary.value)
            .order_by(Message.timestamp.desc())
            .limit(1)
        )
        boundary_msg = boundary_result.scalar_one_or_none()

        # Build query for messages after the boundary (or all if no boundary)
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.role.in_([MessageRole.user.value, MessageRole.assistant.value]))
        )
        if boundary_msg:
            query = query.where(Message.timestamp > boundary_msg.timestamp)
        query = query.order_by(Message.timestamp.asc())

        result = await self.db.execute(query)
        messages = list(result.scalars().all())

        if not messages:
            return "(no previous Q&A)"

        lines = []
        for msg in messages:
            role = "Q" if msg.role == MessageRole.assistant.value else "A"
            lines.append(f"{role}: {msg.content or ''}")

        return "\n".join(lines)

    async def _get_last_question(self, conversation_id: int) -> str:
        """Get the last question asked by the assistant."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.role == MessageRole.assistant.value)
            .order_by(Message.timestamp.desc())
            .limit(1)
        )
        last_message = result.scalar_one_or_none()

        if not last_message:
            return ""

        # If question_card, extract question from metadata
        if last_message.metadata_json and "question" in last_message.metadata_json:
            return last_message.metadata_json["question"]

        return last_message.content[:200]

    def _get_probe_list(self, topic: Optional[str]) -> list[str]:
        """Get probe questions for a topic as a list."""
        if not topic:
            return []

        for content_type_areas in GRAY_AREA_PATTERNS.values():
            for area in content_type_areas:
                if area["topic"].lower() == topic.lower():
                    return area.get("probe_questions", [])

        return []

    def _get_topic_description(self, topic: str, summary_data: dict) -> str:
        """Get topic description from gray area patterns."""
        for content_type_areas in GRAY_AREA_PATTERNS.values():
            for area in content_type_areas:
                if area["topic"].lower() == topic.lower():
                    return area.get("description", "")
        return ""

    # ── JSON parsing ────────────────────────────────────────────────

    def _parse_question_json(self, raw: str) -> dict:
        """Parse JSON from LLM response, with fallback."""
        # Try to find JSON in the response
        raw = raw.strip()

        # Try direct parse
        try:
            data = json.loads(raw)
            return {
                "question": data.get("question", raw),
                "options": data.get("options", []),
            }
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return {
                    "question": data.get("question", raw),
                    "options": data.get("options", []),
                }
            except json.JSONDecodeError:
                pass

        # Try to find any JSON object in the text
        json_match = re.search(r'\{[^{}]*"question"[^{}]*\}', raw, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return {
                    "question": data.get("question", raw),
                    "options": data.get("options", []),
                }
            except json.JSONDecodeError:
                pass

        # Fallback: use raw text as question
        logger.warning("Could not parse question JSON, using raw text: %s", raw[:100])
        return {"question": raw, "options": []}

    def _fallback_question(self, state: ConversationState, language: str) -> dict:
        """Generate a fallback question when LLM fails."""
        topic = state.current_topic or "this topic"
        if language == "nl":
            return {"question": f"Kunt u meer vertellen over {topic}?", "options": []}
        return {"question": f"Can you tell me more about {topic}?", "options": []}

    # ── Unchanged methods ───────────────────────────────────────────

    async def update_decision(
        self, conversation_id: int, decision_index: int, new_value: str
    ) -> None:
        """Update a decision in the summary panel."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one()

        decisions = conversation.summary_data.get("decisions", [])
        if decision_index < len(decisions):
            old_value = decisions[decision_index]
            decisions[decision_index] = new_value

            conversation.summary_data["decisions"] = decisions
            conversation.updated_at = datetime.utcnow()

            system_message = Message(
                conversation_id=conversation_id,
                role=MessageRole.system.value,
                content=f"Decision updated: {old_value} -> {new_value}",
                message_type=MessageType.decision_edit.value,
            )
            self.db.add(system_message)

            await self.db.commit()

    async def complete_discussion(self, conversation_id: int) -> dict:
        """Complete discussion and prepare CONTEXT.md data."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one()

        conversation.status = ConversationStatus.completed.value
        conversation.updated_at = datetime.utcnow()

        await self.db.commit()

        return conversation.summary_data

    # ── Internal helpers (unchanged) ────────────────────────────────

    def _parse_roadmap_for_phase(self, project_type: str, phase_number: int) -> dict:
        """Get phase info from PROJECT_TYPE_PHASES for this project type."""
        phases = PROJECT_TYPE_PHASES.get(project_type, [])
        phase = next((p for p in phases if p["number"] == phase_number), None)
        if not phase:
            return {
                "name": f"Phase {phase_number}",
                "goal": f"Phase {phase_number}",
                "dependencies": [],
            }
        return {
            "name": phase["name"],
            "goal": phase["description"],
            "dependencies": [],
        }

    async def _load_project(self, project_id: int) -> dict:
        """Load project from database."""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            return {"type": "B", "language": "nl"}
        return {
            "type": project.type.value,
            "language": project.language.value,
        }

    def _load_baseline_summary(self, project_id: int) -> Optional[str]:
        """Load baseline summary for Type C/D projects."""
        # TODO: Implement BASELINE.md loading
        return None

    def _build_topic_selection_message(
        self, phase_name: str, gray_areas: list[dict], language: str
    ) -> str:
        """Build initial topic selection message."""
        if language == "nl":
            header = f"Welkom bij de bespreking van {phase_name}!"
            prompt = "Welke onderwerpen wilt u bespreken?"
            discretion = "Resterende onderwerpen aan Claude's beoordeling overlaten"
        else:
            header = f"Welcome to the discussion for {phase_name}!"
            prompt = "Which topics would you like to discuss?"
            discretion = "Mark remaining topics as Claude's Discretion"

        topics_text = "\n".join([
            f"- {area['topic']}: {area['description']}"
            for area in gray_areas
        ])

        return f"""{header}

{prompt}

{topics_text}

- {discretion}
"""

    def _parse_topic_selection(
        self, content: str, available_topics: list[str]
    ) -> tuple[list[str], list[str]]:
        """Parse which topics were selected vs discretion from user message."""
        selected = []
        discretion = []

        normalized = content.lower()
        has_discretion = "discretion" in normalized or "beoordeling" in normalized

        if has_discretion:
            selected = available_topics[:3] if len(available_topics) > 3 else available_topics
            discretion = available_topics[3:] if len(available_topics) > 3 else []
        else:
            selected = available_topics

        return selected, discretion
