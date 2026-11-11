import json
from pathlib import Path

from voice_agent_eval.evaluator import evaluate


ROOT = Path(__file__).parents[1]


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_successful_hvac_fixture_passes():
    result = evaluate(
        load("examples/scenarios/hvac-booking.json"),
        load("examples/transcripts/hvac-success.json"),
    )
    assert result.passed is True
    assert result.review_flags == []


def test_missing_booking_confirmation_fails():
    scenario = {
        "name": "Booking",
        "required_fields": [],
        "require_booking_confirmation": True,
        "booking_confirmation_phrases": ["booking confirmed"],
    }
    transcript = {"messages": [{"role": "assistant", "text": "I have your details."}]}
    result = evaluate(scenario, transcript)
    assert result.passed is False
    assert any(check.name == "booking_confirmation" and not check.passed for check in result.checks)


def test_review_phrase_is_flagged():
    scenario = {"name": "Review", "required_fields": [], "review_phrases": ["guaranteed repair"]}
    transcript = {"messages": [{"role": "assistant", "text": "We offer a guaranteed repair."}]}
    result = evaluate(scenario, transcript)
    assert result.passed is False
    assert result.review_flags == ["guaranteed repair"]


def test_invalid_message_is_rejected():
    scenario = {"name": "Bad input", "required_fields": []}
    transcript = {"messages": [{"role": "assistant", "content": "wrong key"}]}
    try:
        evaluate(scenario, transcript)
    except ValueError as exc:
        assert "text" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
