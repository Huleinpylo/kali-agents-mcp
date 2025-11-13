# Repository Guidelines

> Review `memory.md` for live context and `CONTEXT.MD` for the Pydantic AI reference stack before making changes.

## Project Structure & Module Organization
- CLI entrypoint: `src/cli/main.py` (Typer), with runnable demos in `run_demo.py` and `demo.py`.
- Orchestration logic: `src/agents/supervisor.py` backed by `src/models/` (ML + schemas) and `src/config/settings.py`.
- MCP servers: `src/mcp_servers/{data,network,web}_server.py` sharing persistence helpers in `src/db/connection.py`.
- Tests mirror the tree under `tests/`, e.g., `tests/test_supervisor_agent.py` or `tests/test_web_server_parsers.py`.

## Build, Test, and Development Commands
- Bootstrap once per machine: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt`.
- Run the CLI locally: `kali-agents pentest --target example.com --scope full`.
- Start the SQLite-backed data MCP server after copying `.env.example`: `python -m src.mcp_servers.data_server`.
- Execute the full test pipeline (installs deps, enforces coverage): `./test.sh`.

## Coding Style & Naming Conventions
- Follow PEP 8 with Black’s 88-character limit; run `black src tests` and `isort .` pre-commit.
- Static analysis is mandatory: `flake8 src tests`, `mypy src`, `bandit -r src`.
- Use snake_case for modules/functions, PascalCase for Pydantic models, and document security-relevant code paths.

## Testing Guidelines
- Pytest defaults (`pyproject.toml`) enforce warnings-as-errors, `--cov=src`, and fail-under 80%.
- Mirror the source tree with `test_<area>.py` files so coverage pinpoints regressions.
- For focused suites use markers (`-m "security"`); for reports add `--cov-report=html:htmlcov`.

## Commit & Pull Request Guidelines
- Conventional Commits only (`feat`, `fix`, `security`, etc.); keep scopes tight, e.g., `fix: harden network parser escaping`.
- Branch format: `feature/<summary>` or `fix/<issue-id>`.
- PRs must describe motivation, impacts, linked issues, and executed tests, plus any security considerations.
- Update docs (README, SECURITY.md, AGENTS.md) alongside behavior changes.

## Security & Configuration Tips
- Re-read `SECURITY.md`, `SECURITY_ANALYSIS.md`, and `SECURITY_IMPLEMENTATION.md` before modifying tooling integrations.
- Keep secrets out of git; configure paths via `.env` and ignore generated SQLite/database files.
- Sanitize every argument that reaches MCP servers, leaning on `src/models/core.py` validators.
- Prototype risky tooling through `standalone_supervisor.py` to isolate failures.

## Agent Workflow Notes
- Treat the repo as a production-grade Pydantic AI deployment; align features with the reference stack in `CONTEXT.MD`.
- Start each session by reading `memory.md`, `PROJECT_ANALYSIS.md`, and `DEVELOPMENT_MEMO.md` for current issues, priorities, and regressions.
- Keep config artifacts (`mcp_config.json`, `.env`, future YAML specs) synchronized with code so infra and agents stay deterministic.
- Document reusable playbooks in `examples.md` or adjacent design memos to help both humans and AI agents share skills.
