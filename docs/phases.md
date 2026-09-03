# Phases — Prerequisite Gap Diagnoser
Deadline: Sep 19, 2026, 11:45pm EDT. Today: Sep 3. ~17 days, solo + AI-assisted.

## Phase 0 — Setup (Day 1)
- Repo scaffold: React+Vite frontend, FastAPI backend, basic CI-free local dev loop.
- Pyodide "hello world" running client-side, executing a trivial test case.
- Claude API call working end-to-end from backend with structured/tool-use output.
- **Exit criteria:** you can submit code from the browser, run it in Pyodide, and get one hardcoded LLM response back. Nothing smart yet — just plumbing.

## Phase 1 — Content authoring (Day 2–3)
- Write and **freeze** the 20–25 node concept graph (JSON) for Python fundamentals, culminating in the recursion demo path.
- Write `description`, `mastery_signal`, `micro_lesson`, `teach_back_rubric`, and one test-case-backed `sample_problem` for every node on the demo path (the other nodes need at least `description` + `prerequisites` to look real in the graph view, even if thinner).
- **Exit criteria:** graph JSON is final. No more node edits after this phase — see rules.md §1.

## Phase 2 — Diagnostic engine core (Day 4–7)
- Implement the state machine (`PRESENT_PROBLEM → ... → RESOLVED`) in the backend.
- Implement bounded backward BFS traversal over the graph.
- Wire the three LLM calls (probing question, gap classification, teach-back grading) with structured output + node-ID validation.
- Test the full loop on the recursion path using scripted/manual inputs (no UI yet) — a CLI or Postman-style test harness is fine here.
- **Exit criteria:** you can trigger the full diagnose → teach → teach-back → re-test loop from a script and get correct, grounded results on the recursion path.

## Phase 3 — Frontend integration (Day 8–11)
- Monaco code editor wired to Pyodide execution + test-case checking.
- Graph view (react-flow or custom SVG) rendering the concept graph statically first, then animated to highlight the live traversal path as diagnosis runs.
- Lesson panel + teach-back input wired to backend state.
- **Exit criteria:** a first-time user can go through the entire flow in the browser, on the recursion path, with the graph visibly lighting up during diagnosis.

## Phase 4 — Polish & robustness (Day 12–14)
- Handle edge cases: student answers reasonably but not exactly as expected; LLM returns an invalid node ID (should fail gracefully, not crash the UI).
- Visual polish on the graph animation — this is your single highest-leverage visual for the demo, worth extra time.
- Basic styling pass on the rest of the UI (clean > fancy).
- Deploy: frontend to Vercel, backend to Render/Fly.io. Confirm the deployed version works, not just localhost.
- **Exit criteria:** the deployed app survives a full run-through by someone who has never seen it before (ask a friend to try it cold).

## Phase 5 — Demo & submission (Day 15–17)
- Day 15: write the 2-minute video script (see design.md for the beat-by-beat structure).
- Day 16: record, using the deployed version; have a fallback recorded run ready in case of live-call flakiness.
- Day 17: write the Devpost writeup (problem, solution, tech, what's next), finalize README, submit early — not at 11:44pm.
- **Exit criteria:** submitted, with time to spare in case Devpost has upload issues.

## Cut list (if behind schedule)
In order of what to cut first if time runs short, without breaking the core demo:
1. Thinner nodes outside the recursion demo path (keep only enough for the graph to look populated).
2. Multiple sample problems per node (keep one per node on the demo path).
3. Deployment polish/custom domain — localhost recording is acceptable if deployment slips.
4. Graph animation fanciness — a simple color-change highlight beats no traversal visual at all; don't cut the visual itself, only its polish.

## Never cut
- The end-to-end diagnostic loop working correctly on the recursion path.
- Structured/grounded LLM output (don't fall back to freeform prompting under time pressure — it's the "creative AI" story).
- The 2-minute demo video itself.
