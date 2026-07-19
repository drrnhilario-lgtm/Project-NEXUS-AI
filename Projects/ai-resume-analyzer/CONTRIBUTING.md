# Contributing to NEXUS AI Resume Intelligence Platform

Thank you for helping improve NEXUS AI Resume Intelligence Platform. Contributions should keep the platform transparent, privacy-conscious, fully testable, and useful without paid external services.

## Project philosophy

- Prefer deterministic, explainable analysis over opaque scoring.
- Keep resume processing offline by default.
- Never imply that a score guarantees hiring or reproduces a specific ATS product.
- Preserve user privacy and avoid committing personal resume data.
- Add focused functionality only when its behavior can be explained and tested.

## Before contributing

Search existing issues before opening a duplicate. For substantial changes, open a feature request first so scope and compatibility can be discussed.

Recommended branch names:

- `feature/short-description`
- `fix/short-description`
- `docs/short-description`
- `test/short-description`
- `refactor/short-description`

## Code style

- Follow PEP 8 and use clear snake_case names.
- Add type hints to public functions.
- Use clear Google-style docstrings for public APIs.
- Keep processing in `core/` and presentation in `ui/`.
- Escape dynamic HTML and use `pathlib` for filesystem paths.
- Do not introduce network calls into the offline workflow.

## Testing pull requests

Before opening a pull request, run:

```bash
python -m compileall .
python -m unittest discover -s tests -v
python scripts/validate_release.py
```

Add regression tests for bug fixes and focused tests for new behavior. Use only synthetic data; never submit a real resume, contact details, API keys, or employer-confidential information.

## Reporting issues

Provide a concise title, operating system, Python version, installation method, reproduction steps, expected behavior, actual behavior, and relevant sanitized output. Do not attach private resumes or secrets.

### Bug report template

```markdown
**Summary**

**Environment**
- OS:
- Python version:
- Application version:

**Steps to reproduce**
1.
2.

**Expected behavior**

**Actual behavior**

**Sanitized logs or sample data**
```

Security vulnerabilities must follow [SECURITY.md](SECURITY.md), not the public bug workflow.

## Feature requests

Explain the user problem, proposed behavior, offline/privacy implications, alternatives considered, and how success could be tested. Avoid bundling unrelated changes.

## Documentation

Update README or `docs/` content when behavior, commands, architecture, privacy, limitations, or release requirements change. Keep links relative where practical and use consistent Version 1.0 RC terminology.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Contributions are accepted under the [MIT License](LICENSE).
