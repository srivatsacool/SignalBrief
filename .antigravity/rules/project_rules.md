# SignalBrief Project Rules

## Project
SignalBrief is an open-source, free-first,
AI-powered text analytics platform.

## Development order
1. Jupyter research notebooks
2. Pipeline validation
3. Reusable Python modules
4. Cloudflare backend
5. Web frontend
6. Deployment and monitoring

## Core requirements
- Keep the project open source.
- Avoid mandatory paid services.
- Use configurable domains and sources.
- Keep data collection separate from analysis.
- Keep experimentation separate from production.
- Do not hardcode user preferences.
- Never expose credentials or private user data.
- Never invent sources or article content.

## Engineering requirements
- Write modular, testable code.
- Use type hints where appropriate.
- Document configuration and environment variables.
- Include error handling and structured logging.
- Preserve existing working code.
- Run relevant tests after modifications.
- Do not claim a task is complete without
  verifying its output.

## Workflow
- Work only on the current approved phase.
- Do not start the web application until
  the notebook pipeline is validated.
- Explain architectural changes before
  implementing significant changes.
- Update project documentation after
  completing each milestone.
