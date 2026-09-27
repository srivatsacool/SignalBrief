# Contributing to SignalBrief

Thank you for your interest in contributing to SignalBrief! SignalBrief is an open-source, free-first, notebook-first intelligence reporting platform.

## Guiding Principles

1. **Free-First Constraint**: No component should require a mandatory paid third-party API or service. Everything must operate comfortably within free tiers or open-source local alternatives.
2. **Notebook-First Research**: New analytical approaches, text algorithms, or collectors should be first explored and validated in Jupyter notebooks before refactoring into `src/signalbrief/`.
3. **Traceability**: All synthesized facts must trace back to concrete source URLs.
4. **Privacy & Security**: Never commit user email addresses, private API credentials, or copyrighted article full-text corpora.

## Development Workflow

1. Fork and clone the repository.
2. Create a clean virtual environment:
   ```bash
   uv venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # macOS / Linux
   uv pip install -e ".[dev]"
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Verify tests and code formatting:
   ```bash
   pytest
   ruff check .
   ruff format .
   ```
5. Follow the rules outlined in `.antigravity/rules/`.
6. Open a Pull Request referencing the phase and changes made.
