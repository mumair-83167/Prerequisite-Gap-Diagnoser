# AGENTS.md — Prerequisite Gap Diagnoser

This is the file Antigravity (and any other AGENTS.md-aware tool) reads automatically before touching this repo. Read this in full before generating or editing code. If anything here conflicts with a chat instruction, this file and the docs it points to win — they're the persistent source of truth; chat messages are not.

## Read order (do this first, every session)
1. `memory.md` — current state, decisions already made, open questions. Don't relitigate anything logged here.
2. `prd.md` — what we're building, scope boundaries (MVP vs. out of scope).
3. `architecture.md` — system design, data model, tech stack.
4. `rules.md` — hard constraints. These override convenience or "best practice" defaults.
5. `phases.md` — where we are in the build, what the current phase's exit criteria are.
6. `design.md` — UX flow and demo script, for anything UI-facing.

## Project one-liner
An AI tool that diagnoses the true upstream concept gap behind a failed Python coding exercise (not just the failed concept itself), teaches that specific gap, and verifies understanding via AI-graded teach-back. Built for the Prom Virgo Challenge hackathon (deadline Sep 19, 2026).

## Tech stack (do not substitute without updating this file and memory.md)
- **Frontend**: TypeScript, React, Vite, Monaco Editor, React Flow
- **In-browser execution**: Pyodide — student code always runs client-side in WASM, never server-side `eval`
- **Backend**: Python, FastAPI, Pydantic models for every request/response
- **Database**: SQLite for session/mastery state. Concept graph is a static JSON file, not a DB table.
- **LLM**: Anthropic Claude API, Messages API with tool-use/structured output — every diagnostic LLM call must return validated JSON, never parsed prose
- **Deployment**: Vercel (frontend), Render or Fly.io (backend)

## Repo structure (target)
```
/frontend        React + Vite app
/backend         FastAPI app
  /app
    /prompts     versioned LLM prompt templates — treat like code, review changes
    /graph       concept_graph.json + loader
    /engine      diagnostic state machine
/docs            prd.md, architecture.md, rules.md, phases.md, design.md, memory.md
AGENTS.md        this file
CLAUDE.md        pointer to this file, for Claude Code sessions
.github/copilot-instructions.md   pointer to this file, for Copilot
```

## Non-negotiable rules (full list in rules.md — highlights below)
- Concept graph node list is frozen after Phase 1. No mid-build additions.
- Every diagnostic/grading LLM call is grounded in stored node content (`mastery_signal`, `teach_back_rubric`) and returns structured, validated output. Node IDs from the LLM are checked against the known graph before use.
- Student code correctness is always determined by real Pyodide test execution, never an LLM's opinion.
- Backward graph traversal is bounded to depth 3.
- No secrets committed. API keys via environment variables only.

## How the tools split responsibility
- **Antigravity** (primary): multi-file scaffolding, implementing phases from `phases.md`, running/testing commands in its sandbox. Should treat this file + `/docs` as ground truth before generating code.
- **VS Code**: manual review, debugging, anything Antigravity's sandbox can't do locally (e.g. inspecting deployed environment).
- **GitHub Copilot** (inline, in VS Code): local autocomplete only — small, in-context completions. Should follow the same naming/structure conventions as everything else; see `.github/copilot-instructions.md`.
- **Claude (chat)**: architecture decisions, planning, doc updates, debugging help when Antigravity gets stuck. Not wired into the repo directly — paste context in manually when needed.

## Session protocol
At the **end of every session**, append an entry to `memory.md`'s Session log (what changed, what phase you're now in) and, if a real decision was made (not just implementation detail), add a row to the Decisions log. This is what lets the next session — yours or another tool's — pick up without re-reading the whole chat history.
