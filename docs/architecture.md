# Architecture — Prerequisite Gap Diagnoser

## 1. System overview
Three layers: browser client (UI + code execution), backend (diagnostic reasoning + state), external LLM (Claude API). No server-side code sandboxing is needed because student code runs client-side via Pyodide.

```
Student
  │
  ▼
Browser (client)
 ├─ React UI (code editor, graph view)
 └─ Pyodide sandbox (runs Python in-browser)
  │  code + test results
  ▼
Backend (FastAPI)
 ├─ Diagnostic engine (traversal & repair state machine)
 ├─ Concept graph store (prerequisite links, static content)
 └─ Session DB (SQLite — mastery + history, in-memory OK for demo)
  │  diagnosis, lesson & grading calls
  ▼
Claude API (LLM reasoning)
```

## 2. Components

### 2.1 Frontend (React + Vite)
- **Code editor**: Monaco editor, Python syntax highlighting.
- **Graph view**: `react-flow` or a custom SVG graph rendering the concept graph; nodes light up as the backend traverses backward during diagnosis. This is the single most important UI surface for the demo.
- **Lesson panel**: renders micro-lesson content + teach-back text input.
- **Pyodide sandbox**: loads Python via WebAssembly (`pyodide.js` from CDN), executes student code against stored test cases entirely in-browser. No network round-trip needed for grading correctness — fast, and removes all sandboxing security concerns.

### 2.2 Backend (FastAPI, Python)
- **Diagnostic engine**: a state machine with states `PRESENT_PROBLEM → AWAIT_RESULT → DIAGNOSING → TEACHING → TEACH_BACK → RE_TEST → RESOLVED`.
- **Concept graph store**: a JSON file (or SQLite table) with node schema (see Data model). Loaded once at startup; small enough (20–25 nodes) to keep entirely in memory.
- **Session DB**: tracks current session's traversal path, diagnosed gap, mastery flags. SQLite is enough; no need for Postgres at hackathon scale.
- **LLM orchestration layer**: wraps all Claude API calls, enforces structured JSON output (function-calling / tool-use schema) so responses are parseable and can be validated against known node IDs — this is the main hallucination guardrail.

### 2.3 LLM (Claude API)
Used for exactly three reasoning tasks, each with a narrow, grounded prompt:
1. **Diagnostic question generation** — given a candidate prerequisite node's stored description, generate one short probing question.
2. **Gap classification** — given the student's answer to a probing question, classify `gap_detected: bool`, `confidence: 0-1`. Grounded against the node's stored "what mastery looks like" description, not freeform judgment.
3. **Teach-back grading** — given the student's own-words explanation, grade against a stored rubric for that node; output `understood: bool`, `feedback: str`.

All three calls use Claude's structured/tool-use output mode so responses come back as validated JSON, not prose to parse.

## 3. Data model (concept graph node)
```json
{
  "id": "recursion",
  "name": "Recursion",
  "prerequisites": ["functions", "conditionals"],
  "description": "A function that calls itself, with a base case that stops it.",
  "mastery_signal": "Learner can identify the base case and the recursive case in a given function.",
  "micro_lesson": "Short grounded explanation text + example, used as LLM context, not freely generated from scratch.",
  "sample_problem_id": "factorial_recursive",
  "teach_back_rubric": "Must mention: base case, recursive case, how the call stack unwinds."
}
```

## 4. Diagnostic algorithm (backend logic)
1. Student attempts `sample_problem_id` tied to a target node → Pyodide runs test cases → pass/fail returned to backend.
2. On fail: backend does a bounded backward BFS (depth ≤ 3) over `prerequisites`, nearest-first.
3. For each candidate node, LLM generates one probing question grounded in that node's `description`.
4. Student answers → LLM classifies gap presence, grounded in `mastery_signal`.
5. First node with `gap_detected: true` (or, if none found by depth limit, the deepest node checked) becomes the diagnosed gap — this is the traversal the graph view animates.
6. Backend serves that node's `micro_lesson`.
7. Student writes a teach-back explanation → LLM grades against `teach_back_rubric`.
8. If graded `understood: true`, mark node mastered, return student to the original problem to retry.

## 5. Tech stack
| Layer | Choice | Why |
|---|---|---|
| Frontend | React + Vite | fast iteration, huge ecosystem, Monaco + react-flow both drop in cleanly |
| Code editor | Monaco | industry-standard, minimal setup |
| Graph viz | react-flow (or custom SVG if more control needed for the "lighting up" animation) | built-in pan/zoom, node/edge styling |
| Code execution | Pyodide (WASM) | zero sandboxing infra, runs real Python client-side |
| Backend | FastAPI | fast to write solo, native JSON/Pydantic validation, pairs naturally with a Python-education product |
| LLM | Claude API, tool-use / structured output | grounded, validated diagnostic output |
| Data store | SQLite | zero-ops, sufficient for a session-scoped demo |
| Deployment | Frontend → Vercel; Backend → Render or Fly.io | one-command deploys, free tiers sufficient for a demo |

## 6. Non-goals (see prd.md §6)
No auth, no multi-language support, no persistent cross-session mastery tracking, no server-side sandboxing.
