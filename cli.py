from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from voice_agent_eval.evaluator import evaluate


def _load_json(path: str) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="voice-agent-eval",
        description="Evaluate a voice-agent transcript against a JSON scenario.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("--scenario", required=True)
    evaluate_parser.add_argument("--transcript", required=True)
    evaluate_parser.add_argument("--json-out")

    args = parser.parse_args()
    try:
        result = evaluate(_load_json(args.scenario), _load_json(args.transcript))
        payload = result.to_dict()
        print(f"{'PASS' if result.passed else 'FAIL'}: {result.scenario} ({result.conversation_id})")
        for check in result.checks:
            print(f"  [{'x' if check.passed else ' '}] {check.name}: {check.detail}")
        for flag in result.review_flags:
            print(f"  [!] review phrase detected: {flag}")
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(f"JSON report written to {args.json_out}")
        return 0 if result.passed else 1
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
