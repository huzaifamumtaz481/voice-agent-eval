from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any


FIELD_PATTERNS = {
    "name": [
        r"\bmy name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"\bthis is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    ],
    "phone": [
        r"\b(?:\+?\d[\d\s().-]{7,}\d)\b",
    ],
    "service": [
        r"\b(?:repair|service|installation|maintenance|inspection|tune[- ]?up)\b",
    ],
    "preferred_time": [
        r"\b(?:today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
        r"\d{1,2}(?::\d{2})?\s?(?:am|pm))\b",
    ],
}


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


@dataclass
class Evaluation:
    conversation_id: str
    scenario: str
    passed: bool
    checks: list[Check]
    review_flags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "scenario": self.scenario,
            "passed": self.passed,
            "checks": [asdict(check) for check in self.checks],
            "review_flags": self.review_flags,
        }


def _transcript_text(transcript: dict[str, Any]) -> str:
    messages = transcript.get("messages")
    if not isinstance(messages, list):
        raise ValueError("Transcript must contain a 'messages' array.")
    chunks = []
    for index, message in enumerate(messages):
        if not isinstance(message, dict) or not isinstance(message.get("text"), str):
            raise ValueError(f"Message at index {index} must be an object with string 'text'.")
        role = message.get("role", "unknown")
        chunks.append(f"{role}: {message['text']}")
    return "\n".join(chunks)


def evaluate(scenario: dict[str, Any], transcript: dict[str, Any]) -> Evaluation:
    if not isinstance(scenario.get("required_fields", []), list):
        raise ValueError("'required_fields' must be an array.")
    text = _transcript_text(transcript)
    checks: list[Check] = []

    for field in scenario.get("required_fields", []):
        if field not in FIELD_PATTERNS:
            checks.append(Check(
                name=f"field:{field}",
                passed=False,
                detail=f"Unknown field '{field}'. Supported fields: {', '.join(FIELD_PATTERNS)}.",
            ))
            continue
        matches = [pattern for pattern in FIELD_PATTERNS[field] if re.search(pattern, text, re.I)]
        checks.append(Check(
            name=f"field:{field}",
            passed=bool(matches),
            detail="A configured pattern matched." if matches else
                   "No configured pattern matched; adapt the scenario vocabulary or add a pattern.",
        ))

    if scenario.get("require_booking_confirmation", False):
        phrases = scenario.get("booking_confirmation_phrases", [])
        if not isinstance(phrases, list) or not all(isinstance(p, str) for p in phrases):
            raise ValueError("'booking_confirmation_phrases' must be an array of strings.")
        matched = [phrase for phrase in phrases if phrase.casefold() in text.casefold()]
        checks.append(Check(
            name="booking_confirmation",
            passed=bool(matched),
            detail=f"Matched confirmation phrase(s): {matched}" if matched else
                   "No configured booking confirmation phrase was found.",
        ))

    review_phrases = scenario.get("review_phrases", [])
    if not isinstance(review_phrases, list) or not all(isinstance(p, str) for p in review_phrases):
        raise ValueError("'review_phrases' must be an array of strings.")
    flags = [phrase for phrase in review_phrases if phrase.casefold() in text.casefold()]

    passed = all(check.passed for check in checks) and not flags
    return Evaluation(
        conversation_id=str(transcript.get("conversation_id", "unknown")),
        scenario=str(scenario.get("name", "unnamed")),
        passed=passed,
        checks=checks,
        review_flags=flags,
    )
