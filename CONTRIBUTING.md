# Contributing

Thanks for your interest.

## Setup
1. Create and activate a virtualenv.
2. Install dev dependencies:
   ```bash
   pip install -e .[dev]
   ```

## Quality gates
Before opening a PR:
```bash
pytest
ruff check .
mypy src
python -m build
```

## Style
- Keep code deterministic where possible.
- Add tests with each behavior change.
- Prefer small, reviewable commits.

## Pull requests
- Describe motivation and scope.
- Include validation commands and results.
- Note any limitations or follow-up work.
