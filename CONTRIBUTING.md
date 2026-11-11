# Contributing

Thanks for considering a contribution.

## Before opening an issue
- Search existing issues first.
- Use synthetic or anonymized data only.
- Include the Python version, operating system, command, expected result, and actual result.

## Development setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

## Pull requests
- Keep changes focused.
- Add or update tests for behavior changes.
- Update documentation and examples when formats or CLI behavior changes.
- Do not add network calls or transmit transcript content without explicit design review.
- Explain limitations and false-positive/false-negative risks for new checks.

By contributing, you agree that your contributions are provided under the repository's MIT license.
