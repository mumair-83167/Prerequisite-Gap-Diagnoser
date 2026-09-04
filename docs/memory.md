# Memory — Prerequisite Gap Diagnoser

Living context file. Read this first at the start of every session (human or AI-assisted) before touching code. Update it at the end of every session — this is the source of truth for "where things stand," not any individual chat log.

## Project one-liner
An AI tool that, when a learner fails a Python coding problem, diagnoses the *actual upstream concept gap* (not just the failed concept) via backward traversal of a prerequisite graph, teaches that specific gap, and verifies understanding through AI-graded teach-back — for the Prom Virgo Challenge devpost hackathon.

## Key facts (don't relitigate these)
- Deadline: Sep 19, 2026, 11:45pm EDT.
- Judging: Educational Impact / Creative Use of AI/ML / Technical Execution / Pitch & Demo — 25 pts each.
- Domain: Python fundamentals only. Demo path: recursion → functions → conditionals.
- Solo dev, AI-assisted, generous time budget (~17 days from kickoff).
- Full rationale for these decisions lives in prd.md; don't re-derive them mid-build.

## Decisions log
Append new entries here as they're made — don't overwrite history.

| Date | Decision | Why |
|---|---|---|
| Sep 3 | Domain = programming (Python), not math/other subjects | User preference; also Python enables Pyodide client-side execution, removing sandboxing complexity |
| Sep 3 | Code execution via Pyodide, not server-side sandbox | Zero sandboxing infra/security surface, fast to build solo |
| Sep 3 | Concept graph frozen at ~20-25 nodes before engine work begins | Prevent scope creep eating the timeline (see rules.md §1) |
| Sep 3 | All LLM diagnostic calls use structured/tool-use output, validated against known node IDs | Primary anti-hallucination guardrail (see rules.md §2) |
| Sep 3 | Dev toolchain = Antigravity (primary, agentic) + VS Code (manual/debug) + GitHub Copilot (inline autocomplete) + Claude (planning/architecture, chat) | Matches user's actual workflow; `AGENTS.md` is the canonical context file Antigravity reads, with `CLAUDE.md` and `.github/copilot-instructions.md` as thin pointers so all tools stay in sync |
| Sep 3 | Stack finalized: TypeScript/React/Vite/Monaco/React Flow (frontend), Python/FastAPI/Pydantic (backend), SQLite (session state), Pyodide (client-side code execution), Claude API tool-use (LLM calls) | See AGENTS.md for the full table; no substitutions without updating AGENTS.md + this log |
| Sep 3 | Pyodide runtime via official CDN loader | Eliminates WASM bundler MIME/worker complexity in Vite; verified ~240ms execution |
| Sep 3 | Implemented `.ssd/` governance directory | Standardized proposals across planned, active, and done states |
| Sep 3 | Project Profile: Prototype / Hackathon (via .ai-team) | Calibrates team rigor: focus on security baseline, anti-hallucination, and 1 demo path |
| Sep 3 | Concept graph finalized (21 nodes, 28 edges) and frozen | Hard freeze rule (§1) enforced; zero mid-build additions permitted |
| Sep 4 | Diagnostic engine: formal 7-state FSM + bounded BFS (depth <= 3) + SQLite store | Guarantees deterministic state transitions, zero infinite loops, and persistence |

## Canonical documents (don't duplicate content — link/refer instead)
- `prd.md` — what we're building and why, scope boundaries
- `architecture.md` — system design, tech stack, data model
- `rules.md` — hard constraints that override convenience
- `phases.md` — day-by-day plan, exit criteria, cut list
- `design.md` — UX flow, screen layout, demo video script skeleton

## Glossary
- **Gap node**: the concept graph node diagnosed as the true root cause of a learner's failure.
- **Demo path**: the one fully-polished traversal (recursion → functions → conditionals) built for the video.
- **Teach-back**: the step where the learner explains a concept in their own words and the AI grades it against a stored rubric.
- **Grounded LLM call**: any LLM call whose output is constrained by stored node content (description / mastery_signal / rubric) rather than freeform generation.

## Open questions (resolve before the phase that needs them)
- Exact wording of the recursion-path node content — resolved in Phase 1 (`concept_graph.json`).
- Whether react-flow or custom SVG is used for the graph view — resolved in favor of `@xyflow/react` for smooth state node styling and pan/zoom.
- Fallback behavior if Claude API is slow during the live recording — decide during Phase 4 robustness pass.

## Session log
Use this section as a running changelog so any future session (or a different AI assistant) can catch up fast.

- **Sep 3** — Hackathon selected (Prom Virgo Challenge), idea selected (Prerequisite Gap Diagnoser), domain locked to Python, architecture sketched, all five planning docs (prd/architecture/rules/phases/design) plus this memory file created. No code written yet — next session starts at Phase 0 (repo scaffold).
- **Sep 3 (later)** — Toolchain locked in (Antigravity + VS Code + Copilot + Claude); created `AGENTS.md` (canonical, read by Antigravity), `CLAUDE.md` and `.github/copilot-instructions.md` (thin pointers to AGENTS.md). Still no application code written — next session starts at Phase 0 (repo scaffold), and should be run inside Antigravity so it picks up AGENTS.md automatically.
- **Sep 3 (Phase 0 Complete)** — Executed Proposal `P000: Phase 0 — Core Scaffolding & Plumbing` through all 5 cycles. Built FastAPI backend with Pydantic v2 schemas and structured tool-use diagnostic route; created React + Vite + TypeScript frontend with Monaco Editor and client-side Pyodide WASM runner. All automated test suites passed (pytest 3/3 passed, npm production build passed). Browser subagent validated the end-to-end flow on `http://localhost:5173/` (passing code, failing code with recursion error, and backend diagnostic handshake). `P000` moved to `.ssd/done/`. Ready for Phase 1 (Content authoring).
- **Sep 3 (Phase 1 Complete)** — Executed Proposal `P001: Phase 1 — Content Authoring & Concept Graph Freezing` across all 4 cycles. Authored and froze the 21-node Python fundamentals concept graph (`concept_graph.json`); built DAG validation and caching engine (`loader.py`) and CLI reporting tool (`seed_graph.py`); automated pytest test suite passed 10/10. Bounded backward BFS reachability confirmed (<= 3 hops on demo path). Proposal `P001` moved to `.ssd/done/`. Ready for Phase 2 (Diagnostic state machine & bounded BFS engine).
- **Sep 4 (Phase 2 Complete)** — Executed Proposal `P002: Phase 2 — Diagnostic State Machine & Bounded Traversal Engine` across all 5 cycles. Built SQLite session store (`init_db.py`, `db_models.py`), 7-state FSM (`state_machine.py`), bounded backward BFS engine (`traversal.py`), versioned prompt templates in `prompts/`, structured tool-use Claude engine (`llm_calls.py`), and FastAPI routers (`routes/session.py`, `routes/submit.py`, `routes/diagnose.py`). All automated test suites passed 22/22 (`pytest tests/`). Proposal `P002` moved to `.ssd/done/`. Ready for Phase 3 (Frontend integration & React Flow graph animation).



