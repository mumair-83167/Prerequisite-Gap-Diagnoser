# Rules — Prerequisite Gap Diagnoser

Constraints that govern every decision on this project. When in doubt, these rules win over convenience.

## 1. Scope discipline
- The concept graph node list is **frozen** once written (see phases.md, Day 2). No adding nodes mid-build — resist the urge to make the graph "more complete." Depth and polish on 20–25 nodes beats breadth on 60.
- One fully-polished demo path (recursion → functions → conditionals) is the deliverable. Other paths in the graph can be thinner; they exist to make the graph look real, not to be individually demoed.
- If a feature isn't visible or explainable in a 2-minute video, it's not worth building before submission.

## 2. AI grounding rules (anti-hallucination)
- The LLM never freely decides what a "gap" is — every diagnostic classification is graded against that node's stored `mastery_signal`, never the model's unguided judgment.
- Every LLM call in the diagnostic loop uses structured/tool-use output. Free-text parsing of LLM prose is not allowed anywhere in the diagnostic engine.
- Node IDs returned by the LLM are always validated against the known graph before being used to drive UI state. An unrecognized ID is treated as a failed call, not passed through.
- Micro-lessons are grounded in stored `micro_lesson` content, not generated fully from scratch each time — the LLM elaborates/rephrases, it doesn't invent facts about a concept.

## 3. Code execution rules
- Student code always runs in Pyodide (client-side WASM), never `eval`'d or executed server-side. No server-side sandboxing to build or secure.
- Pass/fail on the original problem is always determined by real test-case execution, never by an LLM's opinion of whether the code "looks right."

## 4. Diagnostic engine rules
- Backward traversal is bounded to depth 3. If no gap is found within that bound, the system says so honestly ("couldn't isolate a single gap — here's the closest match") rather than fabricating a confident answer.
- The traversal path is always shown to the user, live, in the graph view — the reasoning is never hidden. This is a product principle, not just a demo trick: an opaque diagnosis is not trustworthy.

## 5. Engineering rules
- Backend endpoints return typed, validated (Pydantic) responses — no ad hoc dicts.
- Every LLM prompt template lives in one place (`prompts/`), version-controlled and reviewed like code, not inlined ad hoc in request handlers.
- No secrets in the repo. API keys via environment variables only.
- Every commit should leave the app in a runnable state — no "WIP, broken" commits close to the deadline. Solo dev with AI assistance makes this easy to violate; don't.

## 6. Demo & submission rules
- The 2-minute video script is written and rehearsed **before** the last day, not improvised.
- Always have a pre-recorded fallback run in case live LLM calls are slow or flaky during recording.
- Read the Devpost rules page again in the final 48 hours to catch any submission requirement drift (README, licensing, team info, etc.).

## 7. Time-box rules (solo + AI-assisted, 17 days)
- Any single task that's taken 2x its planned time gets cut back to its simplest version rather than pushed through — see phases.md for the specific day-by-day plan and what's cuttable.
- Polish (animations, styling) only happens after the diagnostic loop works end-to-end on the one demo path. Function before form, always.
