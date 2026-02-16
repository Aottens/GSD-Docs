"""Structured output parser for XML-tagged LLM responses."""

import re
from typing import Optional


def parse_question_card(text: str) -> Optional[dict]:
    """
    Parse question card from XML-tagged LLM output.

    Extracts <question>...</question> and optional <options><option>...</option></options> tags.

    Args:
        text: LLM output text containing XML tags

    Returns:
        Dictionary with question and options, or None if no question tag found
    """
    question_match = re.search(r'<question>(.*?)</question>', text, re.DOTALL)
    if not question_match:
        return None

    question = question_match.group(1).strip()
    options = []

    # Parse options if present
    options_match = re.search(r'<options>(.*?)</options>', text, re.DOTALL)
    if options_match:
        option_matches = re.findall(r'<option>(.*?)</option>', options_match.group(1), re.DOTALL)
        options = [opt.strip() for opt in option_matches]

    return {
        "question": question,
        "options": options
    }


def parse_topic_boundary(text: str) -> Optional[dict]:
    """
    Parse topic boundary marker from XML-tagged output.

    Extracts <topic_boundary topic="..." status="..." />

    Args:
        text: LLM output text

    Returns:
        Dictionary with topic and status, or None if no boundary tag found
    """
    boundary_match = re.search(
        r'<topic_boundary\s+topic="([^"]+)"\s+status="([^"]+)"\s*/?>',
        text
    )
    if not boundary_match:
        return None

    return {
        "topic": boundary_match.group(1),
        "status": boundary_match.group(2)
    }


def parse_completion_signal(text: str) -> Optional[str]:
    """
    Parse completion signal from XML-tagged output.

    Extracts <completion_signal>...</completion_signal>

    Args:
        text: LLM output text

    Returns:
        Signal message text or None if no completion tag found
    """
    signal_match = re.search(r'<completion_signal>(.*?)</completion_signal>', text, re.DOTALL)
    if not signal_match:
        return None

    return signal_match.group(1).strip()


def strip_xml_tags(text: str) -> str:
    """
    Remove all recognized XML tags from text.

    Used for message_delta events - frontend sees clean text,
    structured data sent separately via typed events.

    Args:
        text: Text with XML tags

    Returns:
        Text with all recognized XML tags removed
    """
    # Remove question and options tags
    text = re.sub(r'<question>.*?</question>', '', text, flags=re.DOTALL)
    text = re.sub(r'<options>.*?</options>', '', text, flags=re.DOTALL)

    # Remove topic boundary tags
    text = re.sub(r'<topic_boundary[^>]*/?>', '', text)

    # Remove completion signal tags
    text = re.sub(r'<completion_signal>.*?</completion_signal>', '', text, flags=re.DOTALL)

    return text.strip()


class StreamingXMLBuffer:
    """
    Incremental XML parser for SSE streaming.

    Handles partial tags across chunk boundaries and extracts complete
    structured events (question_card, topic_boundary, completion_signal)
    from accumulated buffer.
    """

    def __init__(self):
        """Initialize empty buffer."""
        self.buffer = ""
        self.extracted_positions = []  # Track what we've already extracted

    def feed(self, chunk: str) -> None:
        """
        Add chunk to buffer.

        Args:
            chunk: Text chunk from LLM stream
        """
        self.buffer += chunk

    def extract_events(self) -> list[dict]:
        """
        Extract any complete structured events from buffer.

        Parses buffer for complete XML tags and returns events.
        Marks extracted content to avoid duplicate extraction.

        Returns:
            List of event dictionaries with type and data
        """
        events = []

        # Extract question cards
        for match in re.finditer(r'<question>.*?</question>(?:.*?<options>.*?</options>)?', self.buffer, re.DOTALL):
            start, end = match.span()
            if (start, end) not in self.extracted_positions:
                card = parse_question_card(match.group(0))
                if card:
                    events.append({
                        "type": "question_card",
                        "data": card
                    })
                    self.extracted_positions.append((start, end))

        # Extract topic boundaries
        for match in re.finditer(r'<topic_boundary[^>]*/?>', self.buffer):
            start, end = match.span()
            if (start, end) not in self.extracted_positions:
                boundary = parse_topic_boundary(match.group(0))
                if boundary:
                    events.append({
                        "type": "topic_boundary",
                        "data": boundary
                    })
                    self.extracted_positions.append((start, end))

        # Extract completion signals
        for match in re.finditer(r'<completion_signal>.*?</completion_signal>', self.buffer, re.DOTALL):
            start, end = match.span()
            if (start, end) not in self.extracted_positions:
                signal = parse_completion_signal(match.group(0))
                if signal:
                    events.append({
                        "type": "completion_signal",
                        "data": {"message": signal}
                    })
                    self.extracted_positions.append((start, end))

        return events

    def get_text_content(self) -> str:
        """
        Get non-tag text content from buffer.

        Returns clean text with XML tags removed for message_delta events.

        Returns:
            Clean text content without XML tags
        """
        return strip_xml_tags(self.buffer)

    def clear(self) -> None:
        """Clear buffer and extraction tracking."""
        self.buffer = ""
        self.extracted_positions = []
