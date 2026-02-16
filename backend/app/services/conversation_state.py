"""Conversation state machine for discussion workflow orchestration."""

from dataclasses import dataclass, field
from typing import Optional
import enum


class ConversationPhase(str, enum.Enum):
    """Conversation phase enumeration for state machine."""
    topic_selection = "topic_selection"
    discussion = "discussion"
    check_in = "check_in"
    completion = "completion"


@dataclass
class ConversationState:
    """
    Conversation state machine for discussion workflow.

    Tracks discussion flow with enforced transitions:
    topic_selection -> discussion -> check_in -> discussion -> completion

    Manages topic progression, question rhythm (4-question check-ins),
    decision accumulation, and deferred idea capture.
    """
    phase: ConversationPhase = ConversationPhase.topic_selection
    selected_topics: list[str] = field(default_factory=list)
    completed_topics: list[str] = field(default_factory=list)
    current_topic: Optional[str] = None
    questions_in_current_topic: int = 0
    decisions: list[dict] = field(default_factory=list)
    deferred_ideas: list[dict] = field(default_factory=list)
    is_foundation: bool = False
    discretion_topics: list[str] = field(default_factory=list)

    def start_topic_selection(self) -> None:
        """Transition to topic_selection phase."""
        self.phase = ConversationPhase.topic_selection
        self.current_topic = None
        self.questions_in_current_topic = 0

    def confirm_topics(self, selected: list[str], discretion: list[str]) -> None:
        """
        Confirm topic selection and transition to discussion phase.

        Args:
            selected: Topics the engineer wants to discuss
            discretion: Topics delegated to Claude's discretion
        """
        self.selected_topics = selected
        self.discretion_topics = discretion
        self.phase = ConversationPhase.discussion
        self.current_topic = None
        self.questions_in_current_topic = 0

    def start_topic(self, topic: str) -> None:
        """
        Start discussing a specific topic.

        Args:
            topic: Topic name to start
        """
        self.current_topic = topic
        self.questions_in_current_topic = 0
        self.phase = ConversationPhase.discussion

    def increment_question(self) -> bool:
        """
        Increment question counter for current topic.

        Returns:
            True if check-in time (>= 4 questions), False otherwise
        """
        self.questions_in_current_topic += 1
        return self.questions_in_current_topic >= 4

    def complete_topic(self) -> None:
        """Complete current topic and reset for next topic."""
        if self.current_topic and self.current_topic not in self.completed_topics:
            self.completed_topics.append(self.current_topic)
        self.current_topic = None
        self.questions_in_current_topic = 0
        self.phase = ConversationPhase.discussion

    def start_completion(self) -> None:
        """Transition to completion phase."""
        self.phase = ConversationPhase.completion
        self.current_topic = None

    def next_topic(self) -> Optional[str]:
        """
        Get next unprocessed topic from selected_topics.

        Returns:
            Next topic name or None if all complete
        """
        for topic in self.selected_topics:
            if topic not in self.completed_topics:
                return topic
        return None

    def all_topics_complete(self) -> bool:
        """
        Check if all selected topics are completed.

        Returns:
            True if all selected topics are in completed_topics
        """
        return all(topic in self.completed_topics for topic in self.selected_topics)

    def to_summary_data(self) -> dict:
        """
        Serialize state for DB storage in summary_data JSON column.

        Returns:
            Dictionary representation of state
        """
        return {
            "current_state": {
                "phase": self.phase.value,
                "current_topic": self.current_topic,
                "questions_in_current_topic": self.questions_in_current_topic,
                "is_foundation": self.is_foundation,
            },
            "selected_topics": self.selected_topics,
            "completed_topics": self.completed_topics,
            "discretion_topics": self.discretion_topics,
            "decisions": self.decisions,
            "deferred_ideas": self.deferred_ideas,
        }

    @classmethod
    def from_summary_data(cls, data: dict) -> "ConversationState":
        """
        Reconstruct state from DB JSON data.

        Args:
            data: summary_data dictionary from Conversation model

        Returns:
            ConversationState instance
        """
        current_state = data.get("current_state", {})
        return cls(
            phase=ConversationPhase(current_state.get("phase", "topic_selection")),
            selected_topics=data.get("selected_topics", []),
            completed_topics=data.get("completed_topics", []),
            current_topic=current_state.get("current_topic"),
            questions_in_current_topic=current_state.get("questions_in_current_topic", 0),
            decisions=data.get("decisions", []),
            deferred_ideas=data.get("deferred_ideas", []),
            is_foundation=current_state.get("is_foundation", False),
            discretion_topics=data.get("discretion_topics", []),
        )


def detect_foundation_phase(phase_number: int, phase_goal: str) -> bool:
    """
    Detect if this is a Foundation/intake phase.

    Foundation phase uses open-ended intake conversation instead of
    structured topic cards.

    Args:
        phase_number: Phase number (1-99)
        phase_goal: Phase goal/description text

    Returns:
        True if Foundation phase, False otherwise
    """
    foundation_keywords = ["foundation", "intake", "scope"]
    return (
        phase_number == 1 or
        any(keyword in phase_goal.lower() for keyword in foundation_keywords)
    )
