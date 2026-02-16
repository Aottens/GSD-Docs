"""Verbatim decision extractor with rule-based text processing.

CRITICAL: This service NEVER calls the LLM. It extracts the engineer's exact
words using rule-based processing to honor the "no interpretation" requirement
from v1.0 discuss-phase.md.
"""

import re
from datetime import datetime
from typing import Optional


def is_meta_message(message: str) -> bool:
    """
    Detect if message is conversation control, not an answer.

    Meta messages are conversation navigation commands that shouldn't
    be extracted as decisions.

    Args:
        message: User message text

    Returns:
        True if message is meta (control), False if answer content
    """
    # Normalize: lowercase, strip whitespace
    normalized = message.strip().lower()

    # Empty messages are meta
    if not normalized:
        return True

    # Single-word affirmatives/negatives (check-in responses)
    single_word_meta = {"ja", "nee", "yes", "no", "ok", "okay"}
    if normalized in single_word_meta:
        return True

    # Multi-word control phrases
    control_phrases = [
        "volgende onderwerp", "next topic",
        "meer vragen", "more questions",
        "ga door", "go on", "continue",
        "bevestig", "confirm",
        "volgende", "next",
        "stop", "klaar", "done",
    ]

    for phrase in control_phrases:
        if phrase in normalized:
            return True

    return False


def trim_to_key_sentences(text: str, max_sentences: int = 5) -> str:
    """
    Trim text to key sentences with technical content.

    If text has more than max_sentences, keep the ones with the most
    technical content. This preserves the engineer's words but removes
    excessive filler paragraphs.

    Args:
        text: Input text
        max_sentences: Maximum sentences to keep

    Returns:
        Trimmed text with key technical sentences
    """
    # Split into sentences (basic splitting on . ! ?)
    sentence_pattern = r'[.!?]+\s+'
    sentences = re.split(sentence_pattern, text.strip())

    # Remove empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= max_sentences:
        return text.strip()

    # Score sentences by technical content
    technical_indicators = [
        # Units
        r'\d+\s*°[CF]', r'\d+\s*bar', r'\d+\s*L/min', r'\d+\s*mm',
        r'\d+\s*kW', r'\d+\s*mbar', r'\d+\s*Hz', r'\d+\s*V',
        # Technical terms
        r'\balarm\b', r'\btrip\b', r'\binterlock\b', r'\bvalve\b',
        r'\bsensor\b', r'\bpump\b', r'\bmotor\b', r'\bsetpoint\b',
        r'\bfail-?safe\b', r'\bfail-?closed\b', r'\bfail-?open\b',
        # Numbers (general technical content indicator)
        r'\d+',
    ]

    scored_sentences = []
    for sentence in sentences:
        score = sum(
            1 for pattern in technical_indicators
            if re.search(pattern, sentence, re.IGNORECASE)
        )
        scored_sentences.append((score, sentence))

    # Sort by score (descending), keep top max_sentences
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [s for _, s in scored_sentences[:max_sentences]]

    # Maintain original order
    ordered_top = [s for s in sentences if s in top_sentences]

    return ". ".join(ordered_top) + "."


def extract_verbatim_decision(
    user_message: str,
    current_topic: str,
    question_context: str
) -> Optional[dict]:
    """
    Extract verbatim decision from user answer using rule-based processing.

    CRITICAL: NO LLM in this extraction loop. This is pure rule-based
    extraction to honor the "no interpretation" requirement. We use the
    engineer's exact words, trimmed to key sentences.

    Rule-based extraction steps:
    1. Strip leading/trailing whitespace
    2. Remove obvious filler words at sentence boundaries ONLY
    3. Keep ALL technical content EXACTLY as stated
    4. If very short (< 5 words) after stripping, still capture verbatim

    Args:
        user_message: Engineer's answer text
        current_topic: Current discussion topic
        question_context: The question being answered

    Returns:
        Decision dict with verbatim text, or None if meta-message
    """
    # Check if meta-message first
    if is_meta_message(user_message):
        return None

    # Strip whitespace
    decision_text = user_message.strip()

    # Remove leading filler words (at start of text only)
    leading_fillers = [
        r'^um,?\s+', r'^uh,?\s+', r'^like,?\s+', r'^so,?\s+',
        r'^well,?\s+', r'^basically,?\s+', r'^actually,?\s+',
    ]
    for pattern in leading_fillers:
        decision_text = re.sub(pattern, '', decision_text, flags=re.IGNORECASE)

    # Remove trailing filler phrases (at end of text only)
    trailing_fillers = [
        r',?\s+you know\.?$', r',?\s+I think\.?$',
        r',?\s+right\.?$', r',?\s+I guess\.?$',
    ]
    for pattern in trailing_fillers:
        decision_text = re.sub(pattern, '', decision_text, flags=re.IGNORECASE)

    # Final trim
    decision_text = decision_text.strip()

    # If nothing left after cleaning, it was just filler
    if not decision_text:
        return None

    # Trim to key sentences if very long
    decision_text = trim_to_key_sentences(decision_text, max_sentences=5)

    # Build decision record
    return {
        "topic": current_topic,
        "question": question_context,
        "decision": decision_text,
        "confirmed": False,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
