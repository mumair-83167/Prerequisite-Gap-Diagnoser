# PRD — Prerequisite Gap Diagnoser

## 1. Problem
When a learner fails a programming exercise, most tools respond with "incorrect" or the correct answer. They don't diagnose *why* the learner failed. In hierarchical subjects like programming, a failure on a "hard" concept (recursion, OOP) is very often caused by a shaky grasp of an easier upstream concept (functions, conditionals, variable scope). Generic re-teaching of the failed concept wastes time and doesn't fix the real gap.

## 2. Target user
- Primary: self-taught / early CS students learning Python, working through exercises without a human tutor on hand.
- Secondary (framing for judges): instructors who want a diagnostic tool that surfaces *why* a class is stuck, not just *that* they're stuck.

## 3. Goal (hackathon scope)
Ship a working demo that:
1. Gives the learner a Python coding problem.
2. Detects failure and traces backward through a prerequisite concept graph to find the real root-cause gap.
3. Delivers a short, targeted micro-lesson on that gap.
4. Verifies understanding via a "teach it back to me" step graded by the AI.
5. Returns the learner to the original problem, which they now solve.

## 4. Success metrics
- **Hackathon (primary):** win/place in Prom Virgo Challenge — score high on Educational Impact, Creative Use of AI/ML, Technical Execution, Pitch & Demo.
- **Product (secondary, for judge credibility):** diagnostic accuracy — the tool identifies the correct gap node ≥80% of the time on a curated test set of seeded failure scenarios.
- **Demo:** a first-time viewer understands what the tool does and why it's different within 30 seconds of the video.

## 5. Scope — MVP (must ship)
- One domain: Python fundamentals, ~20–25 concept nodes (variables → operators → conditionals → loops → functions → scope → lists → recursion, etc.)
- One target "flashy" failure scenario fully polished for the demo (recommend: recursion, since the gap chain to functions/base-cases/conditionals is intuitive on camera).
- Code execution in-browser (Pyodide) — no server-side sandboxing needed.
- Backward graph traversal bounded to depth 2–3.
- LLM-driven diagnostic Q&A, micro-lesson generation, and teach-back grading, all grounded in the concept graph's stored content (not freeform).
- A visible graph traversal animation during diagnosis (this is a core demo differentiator, not a nice-to-have).
- Session state only (no auth, no persistence across visits required for demo).

## 6. Out of scope (explicitly, to protect the 17-day timeline)
- Multiple programming languages.
- User accounts, long-term progress tracking, multi-session mastery history.
- Full teacher dashboard / classroom analytics.
- Full-syllabus concept graph (hundreds of nodes) — curated subset only.
- Mobile app; web only.
- Real-time collaboration or multiplayer.

## 7. User stories (MVP)
1. As a learner, I attempt a coding problem and get immediate pass/fail feedback from real code execution, not just an AI opinion.
2. As a learner, when I fail, I'm asked 1–3 short diagnostic questions instead of being shown the answer.
3. As a learner, I see (visually) which concept the system suspects is the actual gap, and why.
4. As a learner, I get a short lesson on just that gap, then I explain it back in my own words.
5. As a learner, once I demonstrate understanding, I'm returned to the original problem and succeed.
6. As a judge watching the demo, I can see the graph light up as it traces backward — the "creative AI reasoning" moment.

## 8. Risks
- LLM hallucinating a wrong diagnosis → mitigate by grounding prompts in the stored graph node content + few-shot examples + structured JSON output validated against known node IDs.
- Scope creep on the concept graph → freeze node list before writing any code (see phases.md).
- Demo flakiness (live LLM calls) → pre-record with a rehearsed, reliable path; have a fallback recorded run if live demo risks timing out.

## 9. Judging alignment (why this scope wins)
| Criterion | How MVP addresses it |
|---|---|
| Educational Impact | Solves a real, well-documented tutoring failure mode (misdiagnosed struggle) |
| Creative Use of AI/ML | Structured backward-chaining diagnosis + explanation grading, not Q&A wrapper |
| Technical Execution | Real graph traversal, real code execution, structured LLM outputs |
| Pitch & Demo | Visual graph traversal gives a dramatic, easy-to-narrate 90-second story |
