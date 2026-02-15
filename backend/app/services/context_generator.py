"""Context generator service for producing CONTEXT.md from discussion decisions."""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.models.conversation import Conversation
from app.prompts.discuss_phase import CONTEXT_MD_TEMPLATE


class ContextGenerator:
    """
    Generates CONTEXT.md from discussion decisions.

    Uses CONTEXT.md template structure with XML-tagged sections:
    - <domain>: Phase boundary from ROADMAP.md goal
    - <decisions>: Implementation decisions organized by topic
    - <specifics>: Exact technical values and references
    - <deferred>: Out-of-scope ideas for other phases

    Enforces 100-line limit (v1.0 Pitfall 7 mitigation).
    """

    def generate(self, conversation: Conversation, project_type: str) -> str:
        """
        Generate CONTEXT.md content from conversation summary_data.

        Uses CONTEXT_MD_TEMPLATE from prompts/discuss_phase.py.
        Enforces 100-line limit (v1.0 Pitfall 7 mitigation).

        Priority if over budget:
        1. Decisions that change what gets written (keep)
        2. Specific technical values (temperatures, capacities, timing) (keep)
        3. General approach notes (compress or omit)

        Args:
            conversation: Conversation with summary_data
            project_type: Project type (A, B, C, or D)

        Returns:
            Generated CONTEXT.md content
        """
        summary_data = conversation.summary_data or {}

        phase_number = summary_data.get("phase_number", conversation.phase_number)
        phase_name = summary_data.get("phase_name", f"Phase {phase_number}")
        phase_goal = summary_data.get("phase_goal", f"Placeholder goal for phase {phase_number}")

        # Build delta scope for Type C/D
        delta_scope = ""
        if project_type in ["C", "D"]:
            delta_scope = "\nDelta from BASELINE.md -- only changes are in scope.\nThe existing system is treated as given. Describe only what changes."

        # Format decisions
        decisions = summary_data.get("decisions", [])
        decisions_text = self._format_decisions(decisions)

        # Format Claude's Discretion items
        discretion_items = summary_data.get("discretion_items", [])
        discretion_text = self._format_discretion_items(discretion_items)

        # Format specifics
        specifics = summary_data.get("specifics", [])
        specifics_text = self._format_specifics(specifics)

        # Format deferred ideas
        deferred_ideas = summary_data.get("deferred_ideas", [])
        deferred_text = self._format_deferred_ideas(deferred_ideas)

        # Generate CONTEXT.md
        date = datetime.now().strftime("%Y-%m-%d")
        phase_slug = f"{phase_number:02d}-{phase_name.lower().replace(' ', '-')}"

        content = CONTEXT_MD_TEMPLATE.format(
            phase_number=phase_number,
            phase_name=phase_name,
            date=date,
            phase_goal=phase_goal,
            delta_scope=delta_scope,
            decisions=decisions_text,
            discretion_items=discretion_text,
            specifics=specifics_text,
            deferred_ideas=deferred_text,
            phase_slug=phase_slug,
        )

        # Enforce 100-line limit
        lines = content.split("\n")
        if len(lines) > 100:
            # TODO: Implement compression logic
            # For now, truncate with warning comment
            content = "\n".join(lines[:97])
            content += "\n\n<!-- WARNING: Content truncated to meet 100-line limit -->"

        return content

    def save(self, project_id: int, phase_number: int, content: str) -> str:
        """
        Write CONTEXT.md to the project's phase directory.

        Args:
            project_id: Project ID
            phase_number: Phase number
            content: CONTEXT.md content

        Returns:
            File path where CONTEXT.md was saved
        """
        # TODO: Get project directory from database or settings
        # For now, use placeholder path
        project_dir = Path(f"projects/{project_id}")
        phase_slug = f"{phase_number:02d}-phase"  # TODO: Get actual phase name

        phase_dir = project_dir / ".planning" / "phases" / phase_slug
        phase_dir.mkdir(parents=True, exist_ok=True)

        context_path = phase_dir / f"{phase_number:02d}-CONTEXT.md"
        context_path.write_text(content, encoding="utf-8")

        return str(context_path)

    def _format_decisions(self, decisions: list) -> str:
        """
        Format decisions section.

        Args:
            decisions: List of decision dictionaries or strings

        Returns:
            Formatted decisions text
        """
        if not decisions:
            return "No specific decisions captured yet."

        formatted = []
        current_topic = None

        for decision in decisions:
            if isinstance(decision, dict):
                topic = decision.get("topic")
                text = decision.get("decision")

                if topic and topic != current_topic:
                    formatted.append(f"\n### {topic}\n")
                    current_topic = topic

                formatted.append(f"- {text}")
            else:
                formatted.append(f"- {decision}")

        return "\n".join(formatted)

    def _format_discretion_items(self, discretion_items: list) -> str:
        """
        Format Claude's Discretion items.

        Args:
            discretion_items: List of discretion item strings

        Returns:
            Formatted discretion text
        """
        if not discretion_items:
            return "No items delegated to Claude's discretion."

        return "\n".join([f"- {item}" for item in discretion_items])

    def _format_specifics(self, specifics: list) -> str:
        """
        Format specifics section.

        Args:
            specifics: List of specific technical values or references

        Returns:
            Formatted specifics text
        """
        if not specifics:
            return "No specific technical values captured yet."

        return "\n".join([f"- {spec}" for spec in specifics])

    def _format_deferred_ideas(self, deferred_ideas: list) -> str:
        """
        Format deferred ideas section.

        Args:
            deferred_ideas: List of deferred idea dictionaries

        Returns:
            Formatted deferred ideas text
        """
        if not deferred_ideas:
            return "None -- discussion stayed within phase scope"

        formatted = []
        for idea in deferred_ideas:
            if isinstance(idea, dict):
                text = idea.get("idea", "")
                phase = idea.get("phase", "")
                formatted.append(f"- {text} -- Phase {phase}")
            else:
                formatted.append(f"- {idea}")

        return "\n".join(formatted)
