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
    foundation_areas_covered: list[str] = field(default_factory=list)
    probes_covered: list[int] = field(default_factory=list)

    # Keywords for Foundation intake area detection (not serialized)
    _FOUNDATION_AREA_KEYWORDS: dict = field(default=None, repr=False, init=False)

    def __post_init__(self):
        self._FOUNDATION_AREA_KEYWORDS = {
            "system_overview": [
                "system", "overview", "process", "installation", "plant",
                "machine", "line", "equipment", "what does", "wat is",
                "beschrijf", "describe", "systeem", "installatie",
            ],
            "reference_docs": [
                "reference", "document", "p&id", "manual", "standard",
                "fds", "specification", "referentie", "documentatie",
                "handleiding", "norm", "standaard",
            ],
            "scope": [
                "scope", "boundary", "in scope", "out of scope",
                "grens", "binnen scope", "buiten scope", "begrenzing",
            ],
            "equipment": [
                "equipment", "grouping", "hierarchy", "area",
                "apparatuur", "groepering", "hiërarchie", "indeling",
                "module", "unit", "station",
            ],
            "terminology": [
                "terminology", "abbreviation", "term", "definition",
                "terminologie", "afkorting", "definitie", "begrip",
                "naming", "convention", "naamgeving",
            ],
        }

    def detect_covered_area(self, question: str, answer: str) -> Optional[str]:
        """Keyword-match Q&A to a foundation intake area."""
        combined = (question + " " + answer).lower()
        for area, keywords in self._FOUNDATION_AREA_KEYWORDS.items():
            if area in self.foundation_areas_covered:
                continue
            if any(kw in combined for kw in keywords):
                return area
        return None

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
        self.probes_covered = []
        self.phase = ConversationPhase.discussion

    def increment_question(self) -> str:
        """
        Increment question counter for current topic.

        Returns:
            'continue' if more questions are needed,
            'check_in' if normal 4-question rhythm reached,
            'force_check_in' if hard cap of 12 questions reached
        """
        self.questions_in_current_topic += 1
        if self.questions_in_current_topic >= 12:
            return "force_check_in"
        if self.questions_in_current_topic >= 4:
            return "check_in"
        return "continue"

    def detect_covered_area_with_fallback(self, question: str, answer: str) -> Optional[str]:
        """
        Keyword-match Q&A to a Foundation intake area, with question-count fallback.

        Tries keyword matching first. If no match is found and >= 2 questions have
        been asked, cycles through uncovered areas in order and marks the next one
        as covered — ensuring progress even when keywords don't match.

        Args:
            question: The last question asked
            answer: The user's answer

        Returns:
            Area name if matched/cycled, None otherwise
        """
        # Try keyword match first
        area = self.detect_covered_area(question, answer)
        if area:
            return area
        # Fallback: after 2+ questions, cycle through uncovered areas
        if self.questions_in_current_topic >= 2:
            all_areas = list(self._FOUNDATION_AREA_KEYWORDS.keys())
            for a in all_areas:
                if a not in self.foundation_areas_covered:
                    return a
        return None

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
                "probes_covered": self.probes_covered,
            },
            "selected_topics": self.selected_topics,
            "completed_topics": self.completed_topics,
            "discretion_topics": self.discretion_topics,
            "decisions": self.decisions,
            "deferred_ideas": self.deferred_ideas,
            "foundation_areas_covered": self.foundation_areas_covered,
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
            foundation_areas_covered=data.get("foundation_areas_covered", []),
            probes_covered=current_state.get("probes_covered", []),
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
