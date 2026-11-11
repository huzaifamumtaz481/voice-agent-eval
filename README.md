# Voice Agent Eval

A small, provider-neutral test harness for evaluating AI voice-agent conversations before deployment.

Voice agents can sound convincing while still failing the task: missing a required booking field, claiming a booking was completed when no confirmation exists, or failing to hand off an unresolved request. Voice Agent Eval turns those requirements into repeatable, inspectable checks.

**Status:** early-stage project (`0.1.0`). This is a starter release; real-world adoption and compatibility claims should only be added after they have been verified.

## What it does

- Validates call transcripts against scenario requirements.
- Checks required information capture (for example, name, phone, service, preferred time).
- Checks whether a booking confirmation phrase is present when a scenario requires it.
- Flags configurable phrases that should trigger human review.
- Produces machine-readable JSON reports and a readable terminal summary.
- Runs locally; no API key or external service is required.

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/YOUR-USERNAME/voice-agent-eval.git
cd voice-agent-eval
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

Evaluate the included example:

```bash
voice-agent-eval evaluate \
  --scenario examples/scenarios/hvac-booking.json \
  --transcript examples/transcripts/hvac-success.json \
  --json-out report.json
```

Run tests:

```bash
pytest
```

## Input format

A transcript is JSON with a `messages` array. Each message has a `role` (`user`, `assistant`, or `tool`) and `text`.

```json
{
  "conversation_id": "demo-001",
  "messages": [
    {"role": "assistant", "text": "Thanks for calling. How can I help?"},
    {"role": "user", "text": "My AC stopped cooling."},
    {"role": "assistant", "text": "May I have your name and phone number?"}
  ]
}
```

A scenario defines the expected outcome:

```json
{
  "name": "HVAC booking",
  "required_fields": ["name", "phone", "service"],
  "require_booking_confirmation": true,
  "booking_confirmation_phrases": ["appointment is confirmed", "you're booked"],
  "review_phrases": ["guaranteed repair", "ignore the safety procedure"]
}
```

The field checks are intentionally transparent keyword/pattern heuristics, not semantic proof. Adapt the scenario vocabulary to your workflow and review flagged calls with a human.

## CLI

```text
voice-agent-eval evaluate --scenario SCENARIO.json --transcript TRANSCRIPT.json [--json-out report.json]
```

Exit codes:
- `0`: all required checks passed and no review flags were found.
- `1`: evaluation completed but one or more checks failed or review flags were found.
- `2`: invalid input or execution error.

## Design principles

1. **Provider-neutral:** transcripts are represented in a simple documented JSON format.
2. **Auditable:** each check explains what it matched and why it passed or failed.
3. **Local-first:** the core evaluator does not transmit call data.
4. **Human oversight:** phrase matches are signals for review, not definitive judgments.
5. **Small surface area:** the first release focuses on transcript QA rather than claiming end-to-end telephony integrations.

## Roadmap

- [ ] JSONL batch evaluation
- [ ] Pluggable transcript import adapters
- [ ] Configurable regex and field extraction rules
- [ ] HTML report output
- [ ] CI example for evaluating a fixture set
- [ ] Integrations contributed and tested by the community

Roadmap items are proposals, not implemented features.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports should include a minimal anonymized fixture and expected behavior. Never submit real customer phone numbers, addresses, recordings, API keys, or other personal data.

## Security and privacy

See [SECURITY.md](SECURITY.md). Use synthetic or properly anonymized transcripts in issues and pull requests. The tool processes local files and does not need network access for its core evaluation.

## License

MIT. See [LICENSE](LICENSE).
