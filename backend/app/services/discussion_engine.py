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
from app.prompts.discuss_phase import (
    detect_content_types,
    get_gray_areas,
    build_system_prompt,
)


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
        4. Generate gray areas for detected content types
        5. Build system prompt
        6. Create Conversation record
        7. Create initial system message with prompt
        8. Create initial assistant message with topic selection card

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

        # Parse ROADMAP.md to get phase goal
        phase_info = self._parse_roadmap_for_phase(project_id, phase_number)
        phase_goal = phase_info["goal"]
        phase_name = phase_info["name"]

        # Detect content types
        content_types = detect_content_types(phase_goal)

        # Generate gray areas
        gray_areas = get_gray_areas(content_types)

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

        # Create conversation
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
                "decisions": [],
                "deferred_ideas": [],
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

        # Create initial assistant message with topic selection
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
        Process user message and stream AI response.

        Steps:
        1. Load conversation with message history
        2. Persist user message
        3. Build messages array for LLM (system prompt + conversation history)
        4. Stream LLM response via stream_complete()
        5. Yield SSE events: message_delta (chunks), then message_complete (full response)
        6. Parse response for structured content (question cards, summary cards)
        7. Persist assistant message with metadata
        8. If topic completed, yield summary_card event with accumulated decisions
        9. Update conversation.summary_data with new decisions

        Args:
            conversation_id: Conversation ID
            content: User message content
            attachments: Optional list of file paths

        Yields:
            SSE event dictionaries with event type and data
        """
        # Load conversation with messages
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one()

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

        # Build messages array for LLM
        messages = await self._build_message_history(conversation_id)

        # Stream LLM response
        full_response = ""
        try:
            async for chunk in self.llm.stream_complete(messages, max_tokens=4096, temperature=0.7):
                full_response += chunk
                # Yield delta event
                yield {
                    "event": "message_delta",
                    "data": {"delta": chunk}
                }

            # Yield complete event
            yield {
                "event": "message_complete",
                "data": {"content": full_response}
            }

            # Parse for structured content
            # TODO: Implement parsing logic for question cards, summary cards

            # Persist assistant message
            assistant_message = Message(
                conversation_id=conversation_id,
                role=MessageRole.assistant.value,
                content=full_response,
                message_type=MessageType.text.value,
            )
            self.db.add(assistant_message)

            # Update conversation timestamp
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

    def _parse_roadmap_for_phase(self, project_id: int, phase_number: int) -> dict:
        """
        Parse project ROADMAP.md to extract phase goal and dependencies.

        Args:
            project_id: Project ID
            phase_number: Phase number

        Returns:
            Dictionary with phase name, goal, and dependencies
        """
        # TODO: Implement ROADMAP.md parsing
        # For now, return placeholder
        return {
            "name": f"Phase {phase_number}",
            "goal": f"Placeholder goal for phase {phase_number}",
            "dependencies": [],
        }

    def _check_phase_dependencies(self, project_id: int, phase_number: int) -> bool:
        """
        Check if phase dependencies are met (SUMMARY.md existence pattern from v1.0).

        Args:
            project_id: Project ID
            phase_number: Phase number

        Returns:
            True if dependencies are met, False otherwise
        """
        # TODO: Implement dependency checking
        return True

    async def _load_project(self, project_id: int) -> dict:
        """
        Load project configuration.

        Args:
            project_id: Project ID

        Returns:
            Project configuration dictionary
        """
        # TODO: Load from database or PROJECT.md
        # For now, return defaults
        return {
            "type": "B",
            "language": "nl",
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
