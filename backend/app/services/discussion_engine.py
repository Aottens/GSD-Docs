"""Discussion engine service for orchestrating discussion workflow."""

import os
from pathlib import Path
from typing import AsyncGenerator, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import Settings
from app.llm.provider import LLMProvider
from app.models.conversation import Conversation, Message, ConversationStatus, MessageRole, MessageType
from app.models.project import Project
from app.models.file import File, FileScope
from app.prompts.discuss_phase import (
    detect_content_types,
    get_gray_areas,
    build_system_prompt,
    PROJECT_TYPE_PHASES,
)
from app.services.conversation_state import ConversationState, ConversationPhase, detect_foundation_phase
from app.services.structured_output_parser import StreamingXMLBuffer, parse_question_card
from app.services.decision_extractor import extract_verbatim_decision, is_meta_message


class DiscussionEngine:
    """
    Orchestrates discussion workflow using v1.0 patterns with backend guardrails.

    Implements the discuss-phase workflow:
    1. Content type detection from phase goal
    2. Gray area generation for detected content types
    3. Chat-optimized system prompt building
    4. Streaming LLM responses with structured content parsing
    5. Decision tracking in conversation summary_data
    """

    def __init__(self, db: AsyncSession, llm: LLMProvider, settings: Settings):
        """
        Initialize discussion engine.

        Args:
            db: Database session
            llm: LLM provider for generating responses
            settings: Application settings
        """
        self.db = db
        self.llm = llm
        self.settings = settings

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

        Args:
            project_id: Project ID
            phase_number: Phase number

        Returns:
            Created conversation with initial messages
        """
        # Load project to get type and language
        project_data = await self._load_project(project_id)
        project_type = project_data.get("type", "B")
        project_language = project_data.get("language", "nl")

        # Get phase info from project type definition
        phase_info = self._parse_roadmap_for_phase(project_type, phase_number)
        phase_goal = phase_info["goal"]
        phase_name = phase_info["name"]

        # Detect if Foundation phase
        is_foundation = detect_foundation_phase(phase_number, phase_goal)

        # Detect content types
        content_types = detect_content_types(phase_goal)

        # Generate gray areas (skip if Foundation)
        gray_areas = [] if is_foundation else get_gray_areas(content_types)

        # Load baseline summary for Type C/D
        baseline_summary = None
        if project_type in ["C", "D"]:
            baseline_summary = self._load_baseline_summary(project_id)

        # Build system prompt
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

        # Initialize conversation state
        state = ConversationState(is_foundation=is_foundation)
        if is_foundation:
            # Foundation phase goes directly to discussion (no topic selection)
            state.phase = ConversationPhase.discussion
            state.current_topic = "Foundation"
        else:
            # Regular phase starts with topic selection
            state.phase = ConversationPhase.topic_selection

        # Create conversation with state
        conversation = Conversation(
            project_id=project_id,
            phase_number=phase_number,
            status=ConversationStatus.active.value,
            title=f"Phase {phase_number}: {phase_name}",
            summary_data={
                "phase_number": phase_number,
                "phase_name": phase_name,
                "content_types": content_types,
                "gray_areas": [area["topic"] for area in gray_areas],
                **state.to_summary_data(),
            },
        )
        self.db.add(conversation)
        await self.db.flush()

        # Create system message
        system_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.system.value,
            content=system_prompt,
            message_type=MessageType.text.value,
        )
        self.db.add(system_message)

        # Create initial assistant message
        if is_foundation:
            # Foundation: open-ended intake greeting
            if project_language == "nl":
                greeting = f"Welkom bij de Foundation bespreking voor dit {project_type} project! Laten we beginnen met het vastleggen van de basis informatie over het systeem en de scope."
            else:
                greeting = f"Welcome to the Foundation discussion for this Type {project_type} project! Let's start by capturing the fundamental information about the system and scope."

            assistant_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.assistant.value,
                content=greeting,
                message_type=MessageType.text.value,
            )
        else:
            # Regular phase: topic selection card
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

    async def send_message(
        self,
        conversation_id: int,
        content: str,
        attachments: Optional[list[str]] = None,
    ) -> AsyncGenerator[dict, None]:
        """
        Process user message and stream AI response with state-aware orchestration.

        Steps:
        1. Load conversation and state
        2. Extract decision from user answer (unless meta-message)
        3. Update state based on phase (topic_selection, discussion, check_in)
        4. Build state-aware LLM prompt
        5. Stream LLM response with XML parsing for structured events
        6. Persist messages and updated state

        Args:
            conversation_id: Conversation ID
            content: User message content
            attachments: Optional list of file paths

        Yields:
            SSE event dictionaries: message_delta, question_card, decision_captured,
            topic_boundary, check_in, message_complete, done
        """
        # Load conversation
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one()

        # Load conversation state
        state = ConversationState.from_summary_data(conversation.summary_data)

        # Persist user message
        user_message = Message(
            conversation_id=conversation_id,
            role=MessageRole.user.value,
            content=content,
            message_type=MessageType.text.value,
            metadata_json={"attachments": attachments} if attachments else None,
        )
        self.db.add(user_message)
        await self.db.commit()

        # Process based on current phase
        if state.phase == ConversationPhase.topic_selection:
            # Parse topic selection
            selected_topics, discretion_topics = self._parse_topic_selection(
                content, conversation.summary_data.get("gray_areas", [])
            )
            state.confirm_topics(selected_topics, discretion_topics)

            # Start first topic
            first_topic = state.next_topic()
            if first_topic:
                state.start_topic(first_topic)
                # Yield topic_boundary event
                yield {
                    "event": "topic_boundary",
                    "data": {"topic_boundary": {"topic": first_topic, "status": "starting"}}
                }

        elif state.phase == ConversationPhase.discussion:
            # Extract decision from user's answer (unless meta-message)
            if not is_meta_message(content) and state.current_topic:
                # Get last assistant question from message history
                last_question = await self._get_last_question(conversation_id)
                decision = extract_verbatim_decision(content, state.current_topic, last_question)

                if decision:
                    # Yield decision_captured event
                    yield {
                        "event": "decision_captured",
                        "data": {"decision": decision}
                    }
                    # Add to state
                    state.decisions.append(decision)

            # Increment question counter
            needs_checkin = state.increment_question()
            if needs_checkin:
                # Transition to check_in phase
                state.phase = ConversationPhase.check_in

        elif state.phase == ConversationPhase.check_in:
            # Parse check-in response
            normalized = content.strip().lower()
            if "next" in normalized or "volgende" in normalized:
                # Complete current topic, move to next
                state.complete_topic()
                # Yield topic_boundary for completed topic
                completed_topic = state.current_topic
                if completed_topic:
                    yield {
                        "event": "topic_boundary",
                        "data": {"topic_boundary": {"topic": completed_topic, "status": "complete"}}
                    }

                next_topic = state.next_topic()
                if next_topic:
                    state.start_topic(next_topic)
                    # Yield topic_boundary for starting next
                    yield {
                        "event": "topic_boundary",
                        "data": {"topic_boundary": {"topic": next_topic, "status": "starting"}}
                    }
                elif state.all_topics_complete():
                    # All topics done, transition to completion
                    state.start_completion()
                    # Yield completion_card event
                    yield {
                        "event": "completion_card",
                        "data": {
                            "completion": {
                                "message": "Alle geselecteerde onderwerpen zijn besproken.",
                                "decisions_count": len(state.decisions),
                                "topics_covered": state.completed_topics
                            }
                        }
                    }
            else:
                # Continue with more questions on current topic
                state.phase = ConversationPhase.discussion

        elif state.phase == ConversationPhase.completion:
            # Handle completion phase interactions
            normalized = content.strip().lower()
            if "meer" in normalized or "add more" in normalized.lower():
                # Transition back to discussion (allow freeform questions)
                state.phase = ConversationPhase.discussion
                state.current_topic = "Additional Topics"
            elif "bevestig" in normalized or "confirm" in normalized.lower():
                # Frontend will call preview-context endpoint
                # No action needed here, just acknowledge
                pass

        # Build state-aware prompt
        messages = await self._build_message_history(conversation_id)
        state_context = self._build_state_aware_prompt(state, content, conversation.project_id)
        if state_context:
            messages.append({"role": "system", "content": state_context})

        # Stream LLM response with XML parsing
        full_response = ""
        buffer = StreamingXMLBuffer()
        completion_signal_detected = False

        try:
            async for chunk in self.llm.stream_complete(messages, max_tokens=4096, temperature=0.7):
                full_response += chunk
                buffer.feed(chunk)

                # Extract any structured events
                for event in buffer.extract_events():
                    yield event
                    # Check if this is a completion_signal event (Foundation phase)
                    if event.get("event") == "completion_signal" or event.get("type") == "completion_signal":
                        completion_signal_detected = True

                # Yield text content as message_delta (without XML tags)
                text_content = buffer.get_text_content()
                if text_content and text_content != full_response:
                    # Only yield new text since last extraction
                    yield {
                        "event": "message_delta",
                        "data": {"delta": chunk}
                    }

            # Foundation phase completion detection
            if state.is_foundation and completion_signal_detected:
                # LLM determined intake is thorough enough
                state.start_completion()
                yield {
                    "event": "completion_card",
                    "data": {
                        "completion": {
                            "message": "Foundation bespreking is afgerond. De AI heeft genoeg informatie verzameld.",
                            "decisions_count": len(state.decisions),
                            "topics_covered": ["Foundation"]
                        }
                    }
                }

            # Yield complete event
            yield {
                "event": "message_complete",
                "data": {"final": full_response}
            }

            # Persist assistant message
            assistant_message = Message(
                conversation_id=conversation_id,
                role=MessageRole.assistant.value,
                content=full_response,
                message_type=MessageType.text.value,
            )
            self.db.add(assistant_message)

            # Update conversation with new state
            conversation.summary_data.update(state.to_summary_data())
            conversation.updated_at = datetime.utcnow()

            await self.db.commit()

            # Yield done event
            yield {
                "event": "done",
                "data": {}
            }

        except Exception as e:
            # Yield error event
            yield {
                "event": "error",
                "data": {"error": str(e)}
            }
            raise

    async def update_decision(
        self, conversation_id: int, decision_index: int, new_value: str
    ) -> None:
        """
        Update a decision in the summary panel.

        Steps:
        1. Load conversation
        2. Update summary_data at decision_index
        3. Append system message: "Decision updated: [old] -> [new]"
        4. Persist changes

        Args:
            conversation_id: Conversation ID
            decision_index: Index of decision to update
            new_value: New decision value
        """
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one()

        # Update decision in summary_data
        decisions = conversation.summary_data.get("decisions", [])
        if decision_index < len(decisions):
            old_value = decisions[decision_index]
            decisions[decision_index] = new_value

            conversation.summary_data["decisions"] = decisions
            conversation.updated_at = datetime.utcnow()

            # Add system message about update
            system_message = Message(
                conversation_id=conversation_id,
                role=MessageRole.system.value,
                content=f"Decision updated: {old_value} -> {new_value}",
                message_type=MessageType.decision_edit.value,
            )
            self.db.add(system_message)

            await self.db.commit()

    async def complete_discussion(self, conversation_id: int) -> dict:
        """
        Complete discussion and prepare CONTEXT.md data.

        Steps:
        1. Mark conversation as completed
        2. Return summary_data for CONTEXT.md generation

        Args:
            conversation_id: Conversation ID

        Returns:
            Summary data dictionary for CONTEXT.md generation
        """
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one()

        conversation.status = ConversationStatus.completed.value
        conversation.updated_at = datetime.utcnow()

        await self.db.commit()

        return conversation.summary_data

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
        """
        Load baseline summary for Type C/D projects.

        Args:
            project_id: Project ID

        Returns:
            Baseline summary text or None
        """
        # TODO: Implement BASELINE.md loading
        return None

    def _build_topic_selection_message(
        self, phase_name: str, gray_areas: list[dict], language: str
    ) -> str:
        """
        Build initial topic selection message.

        Args:
            phase_name: Phase name
            gray_areas: Gray area topics
            language: Project language (nl or en)

        Returns:
            Formatted message text
        """
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

    async def _build_message_history(self, conversation_id: int) -> list[dict]:
        """
        Build message history for LLM.

        Args:
            conversation_id: Conversation ID

        Returns:
            List of message dictionaries for LLM
        """
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp)
        )
        messages = result.scalars().all()

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role in [MessageRole.system.value, MessageRole.user.value, MessageRole.assistant.value]
        ]

    def _build_state_aware_prompt(
        self, state: ConversationState, user_message: str, project_id: int
    ) -> Optional[str]:
        """
        Build additional context for LLM based on current conversation state.

        Includes: current topic, remaining topics, questions asked so far,
        check-in instruction if applicable, reference file summaries for Foundation.

        Args:
            state: Current conversation state
            user_message: User's latest message
            project_id: Project ID for loading reference files

        Returns:
            Context string to inject, or None if no additional context needed
        """
        context_parts = []

        # Current topic context
        if state.current_topic:
            context_parts.append(f"Current topic: {state.current_topic}")
            context_parts.append(f"Questions asked on this topic: {state.questions_in_current_topic}")

        # Remaining topics
        if state.selected_topics:
            remaining = [t for t in state.selected_topics if t not in state.completed_topics]
            if remaining:
                context_parts.append(f"Remaining topics: {', '.join(remaining)}")

        # Check-in instruction
        if state.phase == ConversationPhase.check_in:
            context_parts.append(
                "Check-in time: Ask if the engineer wants more questions on this topic or to move to the next."
            )

        # Reference files for Foundation phase
        if state.is_foundation:
            ref_summary = self._load_reference_files(project_id)
            if ref_summary:
                context_parts.append(f"Reference files available:\n{ref_summary}")

        if not context_parts:
            return None

        return "\n\n".join(context_parts)

    def _load_reference_files(self, project_id: int) -> Optional[str]:
        """
        Load uploaded reference files for the project from file system.

        Returns a summary string of available files and their content previews
        (first 500 chars each). Max 3000 chars total to avoid prompt bloat.

        This content gets injected into Foundation phase prompts so AI can ask:
        "I see from [document] that... is this still current?"

        Args:
            project_id: Project ID

        Returns:
            Summary string of files and content, or None if no files
        """
        # Note: This is a synchronous call in an async function
        # For now, return None as file loading implementation requires
        # reading from filesystem which should be done properly
        # TODO: Implement proper async file reading
        return None

    def _parse_topic_selection(
        self, content: str, available_topics: list[str]
    ) -> tuple[list[str], list[str]]:
        """
        Parse which topics were selected vs discretion from user message.

        Handles both structured (JSON from TopicSelectionCard) and freeform
        ("I want to discuss topics 1, 3, 5") responses.

        Args:
            content: User message content
            available_topics: List of available topic names

        Returns:
            Tuple of (selected_topics, discretion_topics)
        """
        # Simple parsing: assume user message contains topic names or numbers
        # More sophisticated parsing can be added based on frontend format

        selected = []
        discretion = []

        # Check if "discretion" or "beoordeling" mentioned
        normalized = content.lower()
        has_discretion = "discretion" in normalized or "beoordeling" in normalized

        # For now, assume all topics are selected unless discretion mentioned
        if has_discretion:
            # User wants to delegate some topics
            # Simple heuristic: if they mention specific topics, those are selected
            # Otherwise, mark all as selected for now (can be refined)
            selected = available_topics[:3] if len(available_topics) > 3 else available_topics
            discretion = available_topics[3:] if len(available_topics) > 3 else []
        else:
            # All topics selected
            selected = available_topics

        return selected, discretion

    async def _get_last_question(self, conversation_id: int) -> str:
        """
        Get the last question asked by the assistant.

        Used for decision extraction context.

        Args:
            conversation_id: Conversation ID

        Returns:
            Last assistant question text, or empty string if not found
        """
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

        # Try to extract question from content
        # If message contains <question> tag, extract it
        parsed = parse_question_card(last_message.content)
        if parsed:
            return parsed["question"]

        # Otherwise return the full content (truncated if needed)
        return last_message.content[:200]
