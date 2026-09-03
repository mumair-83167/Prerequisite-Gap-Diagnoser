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
- Exact wording of the recursion-path node content — owner: content authoring pass, Phase 1.
- Whether react-flow or custom SVG is used for the graph view — decide early Phase 3, don't block Phase 2 on this.
- Fallback behavior if Claude API is slow during the live recording — decide during Phase 4 robustness pass.

## Session log
Use this section as a running changelog so any future session (or a different AI assistant) can catch up fast.

- **Sep 3** — Hackathon selected (Prom Virgo Challenge), idea selected (Prerequisite Gap Diagnoser), domain locked to Python, architecture sketched, all five planning docs (prd/architecture/rules/phases/design) plus this memory file created. No code written yet — next session starts at Phase 0 (repo scaffold).
- **Sep 3 (later)** — Toolchain locked in (Antigravity + VS Code + Copilot + Claude); created `AGENTS.md` (canonical, read by Antigravity), `CLAUDE.md` and `.github/copilot-instructions.md` (thin pointers to AGENTS.md). Still no application code written — next session starts at Phase 0 (repo scaffold), and should be run inside Antigravity so it picks up AGENTS.md automatically.
