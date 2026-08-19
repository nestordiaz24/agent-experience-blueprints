# Contributing

Thank you for improving Agent Experience Blueprints.

## Development setup

Prerequisites:

- Python 3.12
- Node.js 22 LTS for web samples added in later milestones
- Git

Create a virtual environment and install the Python development dependencies:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the current checks before opening a pull request:

```powershell
python -m ruff check packages tests
python -m mypy packages/agent_core
python -m pytest
```

## Pull requests

- Keep provider execution separate from channel rendering.
- Use typed results; do not render arbitrary objects with `str()` or join heterogeneous results with newlines.
- Add focused tests for behavior and failure paths.
- Use only synthetic data, reserved domains, and placeholder tenant values.
- Update the decision log when a change establishes a repository-wide architectural rule.

By participating, you agree to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Contributions are licensed under the repository's MIT license.
