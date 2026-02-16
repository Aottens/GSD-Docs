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

        # Enforce 100-line limit with compression
        lines = content.split("\n")
        if len(lines) > 100:
            content = self._compress_to_100_lines(content, decisions)

        return content

    def generate_preview(self, conversation_summary_data: dict, project_type: str) -> str:
        """
        Generate CONTEXT.md preview from conversation summary_data without saving to disk.

        Used by preview endpoint to show engineer what CONTEXT.md will contain
        before finalizing the discussion.

        Args:
            conversation_summary_data: Summary data from Conversation model
            project_type: Project type (A, B, C, or D)

        Returns:
            Generated CONTEXT.md content string
        """
        phase_number = conversation_summary_data.get("phase_number", 1)
        phase_name = conversation_summary_data.get("phase_name", f"Phase {phase_number}")
        phase_goal = conversation_summary_data.get("phase_goal", f"Placeholder goal for phase {phase_number}")

        # Build delta scope for Type C/D
        delta_scope = ""
        if project_type in ["C", "D"]:
            delta_scope = "\nDelta from BASELINE.md -- only changes are in scope.\nThe existing system is treated as given. Describe only what changes."

        # Format decisions
        decisions = conversation_summary_data.get("decisions", [])
        decisions_text = self._format_decisions(decisions)

        # Format Claude's Discretion items
        discretion_items = conversation_summary_data.get("discretion_items", [])
        discretion_text = self._format_discretion_items(discretion_items)

        # Format specifics
        specifics = conversation_summary_data.get("specifics", [])
        specifics_text = self._format_specifics(specifics)

        # Format deferred ideas
        deferred_ideas = conversation_summary_data.get("deferred_ideas", [])
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

        # Enforce 100-line limit with compression
        lines = content.split("\n")
        if len(lines) > 100:
            content = self._compress_to_100_lines(content, decisions)

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
        Format decisions section with verbatim text from engineer.

        New verbatim decision format (from Plan 10.1-03):
        - Decisions are dicts: {"topic": str, "question": str, "decision": str, "confirmed": bool, "notes": str?, "timestamp": str}
        - Group by topic
        - Only include confirmed decisions in main section
        - Unconfirmed decisions get "## Pending Review" section
        - Use engineer's EXACT decision text (verbatim -- do NOT summarize or rephrase)
        - If notes exist, append as sub-bullet: "  - _Note: {notes}_"

        Args:
            decisions: List of decision dictionaries or strings

        Returns:
            Formatted decisions text
        """
        if not decisions:
            return "No specific decisions captured yet."

        # Separate confirmed and unconfirmed decisions
        confirmed = []
        unconfirmed = []

        for decision in decisions:
            if isinstance(decision, dict):
                if decision.get("confirmed", False):
                    confirmed.append(decision)
                else:
                    unconfirmed.append(decision)
            else:
                # Legacy string format -- treat as confirmed
                confirmed.append({"decision": decision, "confirmed": True})

        # Format confirmed decisions by topic
        formatted = []
        current_topic = None

        for decision in confirmed:
            topic = decision.get("topic")
            text = decision.get("decision")
            notes = decision.get("notes")

            if topic and topic != current_topic:
                formatted.append(f"\n### {topic}\n")
                current_topic = topic

            formatted.append(f"- {text}")
            if notes:
                formatted.append(f"  - _Note: {notes}_")

        # Add unconfirmed section if any exist
        if unconfirmed:
            formatted.append("\n## Pending Review\n")
            for decision in unconfirmed:
                topic = decision.get("topic")
                text = decision.get("decision")
                formatted.append(f"- **[{topic}]** {text}")

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

    def _compress_to_100_lines(self, content: str, decisions: list) -> str:
        """
        Compress CONTEXT.md to meet 100-line limit.

        Compression priority (from plan):
        1. Decisions that change what gets written (KEEP -- look for keywords: "should", "must", "will", "not", "instead")
        2. Specific technical values -- numbers, units, temperatures, capacities (KEEP)
        3. General approach notes without specific values (COMPRESS -- combine into single bullet per topic)
        4. Use tables for parameter values when multiple numeric decisions exist for same topic

        Args:
            content: Original CONTEXT.md content
            decisions: Decision list for re-formatting

        Returns:
            Compressed content under 100 lines
        """
        import re

        # Parse content into sections
        lines = content.split("\n")

        # Extract header (everything before <decisions>)
        header_end = 0
        for i, line in enumerate(lines):
            if "<decisions>" in line:
                header_end = i + 1
                break

        header = lines[:header_end]

        # Extract footer (everything after </decisions>)
        footer_start = len(lines)
        for i, line in enumerate(lines):
            if "</deferred>" in line:
                footer_start = i + 1
                break

        footer = lines[footer_start:]

        # Re-format decisions with compression
        compressed_decisions = self._compress_decisions(decisions)

        # Rebuild content
        compressed = header + [compressed_decisions] + footer

        # If still over 100 lines, truncate footer
        if len(compressed) > 100:
            available_for_footer = 100 - len(header) - len([compressed_decisions])
            if available_for_footer > 0:
                compressed = header + [compressed_decisions] + footer[:available_for_footer]
            else:
                compressed = header + [compressed_decisions]

        return "\n".join(compressed)

    def _compress_decisions(self, decisions: list) -> str:
        """
        Compress decisions with priority-based filtering.

        Priority 1: Decisions with prescriptive keywords (should, must, will, not, instead)
        Priority 2: Decisions with numeric values (temperatures, capacities, etc.)
        Priority 3: General approach notes (compress into single line per topic)

        Args:
            decisions: List of decision dicts

        Returns:
            Compressed decisions text
        """
        import re

        if not decisions:
            return "No specific decisions captured yet."

        # Keywords for Priority 1 (prescriptive decisions)
        prescriptive_keywords = r'\b(should|must|will|shall|not|instead|never|always|required|mandatory)\b'

        # Pattern for Priority 2 (numeric values with units)
        numeric_pattern = r'\b\d+\.?\d*\s*(°C|°F|K|bar|psi|MPa|L/min|m³/h|kg/h|mm|cm|m|%|A|V|W|Hz|rpm)\b'

        # Classify decisions by priority
        priority_1 = []
        priority_2 = []
        priority_3 = []

        for decision in decisions:
            if not isinstance(decision, dict):
                continue

            if not decision.get("confirmed", False):
                continue  # Skip unconfirmed (handled separately)

            text = decision.get("decision", "")

            # Check for prescriptive keywords
            if re.search(prescriptive_keywords, text, re.IGNORECASE):
                priority_1.append(decision)
            # Check for numeric values
            elif re.search(numeric_pattern, text):
                priority_2.append(decision)
            else:
                priority_3.append(decision)

        # Build compressed output
        formatted = []
        current_topic = None

        # Priority 1: Keep all prescriptive decisions
        for decision in priority_1:
            topic = decision.get("topic")
            text = decision.get("decision")

            if topic and topic != current_topic:
                formatted.append(f"\n### {topic}\n")
                current_topic = topic

            formatted.append(f"- {text}")

        # Priority 2: Keep all numeric decisions, consider table format if many
        numeric_by_topic = {}
        for decision in priority_2:
            topic = decision.get("topic", "General")
            if topic not in numeric_by_topic:
                numeric_by_topic[topic] = []
            numeric_by_topic[topic].append(decision.get("decision"))

        for topic, values in numeric_by_topic.items():
            if topic != current_topic:
                formatted.append(f"\n### {topic}\n")
                current_topic = topic

            # If 3+ numeric values for same topic, consider table format
            if len(values) >= 3:
                formatted.append("\n| Parameter | Value |")
                formatted.append("| --- | --- |")
                for value in values:
                    # Extract parameter name and value
                    parts = value.split(",", 1)
                    if len(parts) == 2:
                        formatted.append(f"| {parts[0].strip()} | {parts[1].strip()} |")
                    else:
                        formatted.append(f"| Value | {value} |")
            else:
                for value in values:
                    formatted.append(f"- {value}")

        # Priority 3: Compress general notes into single bullet per topic
        general_by_topic = {}
        for decision in priority_3:
            topic = decision.get("topic", "General")
            if topic not in general_by_topic:
                general_by_topic[topic] = []
            general_by_topic[topic].append(decision.get("decision"))

        for topic, notes in general_by_topic.items():
            if topic != current_topic:
                formatted.append(f"\n### {topic}\n")
                current_topic = topic

            # Combine all notes into single bullet
            if len(notes) == 1:
                formatted.append(f"- {notes[0]}")
            else:
                combined = "; ".join(notes)
                formatted.append(f"- General approach: {combined}")

        return "\n".join(formatted)
