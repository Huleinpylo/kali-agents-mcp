# Repository Memory Log

_Last updated: 2025-11-13_

This file captures the latest engineering context so humans and AI assistants can pick up work without re-discovering prior findings. Update it at the end of every significant session.

## Session Snapshot
- Hardened contributor guidance by adding `AGENTS.md` and `CONTEXT.MD`, plus cross-links from README/CONTRIBUTING.
- Established this `memory.md` log so future sessions have an authoritative context anchor.
- Added CHANGELOG tracking, security issue template, `.editorconfig`, Ruff config, and FastAPI scaffolding for network/web scans (see `src/api`).
- Landed FastAPI endpoint tests in `tests/test_api_endpoints.py` to validate health, network/web scans, and API-key enforcement.

## Current Test Failures
- None recorded. Run `./test.sh` (full suite) before merging and document any failures or flakes here with reproduction steps.

## Known Issues & Root Causes
- _None tracked yet._ Add entries such as `[#123] supervisor retry loop flakes under high latency` once confirmed.

## Recent Changes & Impact
- **2025-11-13** – Repository guidelines added; no runtime impact but docs now guide AI assistants toward correct workflows.
- **2025-11-13** – API groundwork shipped (`src/api/main.py`, routers, security helpers); README documents how to run `uvicorn` for web/network scans.

## Action Plan & Priorities
1. Keep automation runners (e.g., demos, supervisor) referencing `AGENTS.md`/`CONTEXT.MD` so AI copilots ingest the latest expectations.
2. When bugs or security findings surface, log detection date, affected modules, and mitigation status here.
3. Record coverage dips (<80%) or perf regressions immediately, along with owners.

## Testing & Verification Notes
- Default workflow: activate `venv`, install requirements, run `./test.sh`.
- Use targeted `pytest -k "<pattern>" -m "not slow"` for quick iterations; capture deviations from this flow here.

## Context From Previous Sessions
- _No legacy context available beyond the documentation refresh recorded above._
