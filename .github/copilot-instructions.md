# Copilot instructions

This project's full context and rules live in `AGENTS.md` at the repo root — treat it as authoritative for naming, structure, and constraints, even though Copilot only sees local file context most of the time.

Key conventions to follow in every suggestion:
- Backend: Python, FastAPI, Pydantic models for all request/response types — no raw dicts crossing an API boundary.
- Frontend: TypeScript, React, functional components only.
- Any code that calls the Claude API must use structured/tool-use output — never suggest parsing free-text LLM responses.
- Never suggest executing student-submitted code server-side (e.g. `eval`, `exec`, `subprocess`). All student code execution happens client-side via Pyodide.
- Never hardcode API keys or secrets — always read from environment variables.
- Concept graph content (`backend/app/graph/concept_graph.json`) is frozen after Phase 1 — don't suggest new nodes or restructuring it without being explicitly asked.

For anything beyond local autocomplete — new files, architecture questions, multi-step tasks — defer to Antigravity or Claude rather than generating large blocks inline.
