# Design — Prerequisite Gap Diagnoser

## 1. Design principles
- **Show the reasoning, don't just state the result.** The graph traversal must always be visible — it's both the pedagogical honesty principle and the demo's best visual.
- **One screen, evolving state** — avoid multi-page navigation. The learner (and the judge watching) should never lose context by clicking to a new page mid-flow.
- **Function before form.** Clean and legible beats decorative. No gradients or busy styling that competes with the graph visualization for attention.

## 2. Core screen layout (single view, three zones)
```
┌─────────────────────────────────────────────┐
│  Top: problem statement + code editor        │
│  (Monaco, with Run button, pass/fail banner) │
├───────────────────────┬───────────────────────┤
│  Left: concept graph   │  Right: dynamic panel │
│  (static, highlights   │  (probing question /  │
│   during diagnosis)    │   micro-lesson /      │
│                        │   teach-back input)   │
└───────────────────────┴───────────────────────┘
```

## 3. User flow (state → screen behavior)
1. **PRESENT_PROBLEM** — problem statement + empty editor. Graph shown dimmed/static in the background, target node subtly highlighted (gray).
2. **AWAIT_RESULT** — student runs code; Pyodide executes; pass/fail banner appears.
3. **DIAGNOSING** — on fail, right panel shows a probing question; graph animates — the node currently being checked pulses/highlights (e.g., amber), edges traversed so far shown solid, not-yet-checked prerequisite edges shown dashed/gray.
4. **TEACHING** — once a gap is found, that node turns a distinct color (e.g., coral) and stays highlighted; right panel shows the micro-lesson.
5. **TEACH_BACK** — right panel becomes a text input: "explain this back in your own words."
6. **RE_TEST** — on successful teach-back, node turns "mastered" color (teal/green), right panel confirms and returns focus to the original editor/problem.
7. **RESOLVED** — student re-attempts the original problem; passes; brief success state shown (e.g., all traversed nodes now shown teal, indicating the repaired chain).

## 4. Visual encoding on the graph (color = state, not category)
| State | Color |
|---|---|
| Not yet checked | Gray |
| Currently being probed | Amber (active) |
| Diagnosed gap | Coral |
| Taught + mastered | Teal/green |
| Target (original) node | Outlined/bold border throughout |

This mirrors the "color encodes meaning" principle used in the architecture diagram — consistent visual language across your product and your pitch deck reinforces the story.

## 5. Demo video structure (2 minutes, beat by beat)
This is the actual script skeleton — write the real lines during Phase 5.
1. **0:00–0:15 — Hook.** State the problem in one line: generic tutoring tools tell you *that* you're wrong, not *why*. Show a student stuck on recursion.
2. **0:15–0:45 — Diagnosis in action.** Student fails the recursion problem. Cut to the graph view. Narrate as it traces backward: "it's not checking recursion again — it's checking whether the real gap is functions, or conditionals, or something else." Show the amber pulse moving node to node.
3. **0:45–1:10 — The catch.** Graph lands on the true gap (e.g., "distribution of function calls" / whatever the scripted demo path is). Node turns coral. Show the targeted micro-lesson appearing — emphasize it's short and specific, not a re-explanation of recursion.
4. **1:10–1:35 — Teach-back.** Student types an explanation. AI grades it, node turns teal. Narrate: this isn't just marking right/wrong — it's checking genuine understanding, grounded in a rubric, not vibes.
5. **1:35–1:55 — Payoff.** Cut back to the original problem. Student re-attempts it — passes. This closes the loop the viewer opened at 0:15.
6. **1:55–2:00 — Close.** One line on what's next (more subjects, teacher-facing gap analytics across a class) — shows judges you thought past the MVP without over-promising it as already built.

## 6. Content authoring guidelines (for the concept graph text)
- `description`: 1–2 sentences, plain language, no jargon beyond what's needed.
- `mastery_signal`: written as an observable behavior ("can identify X in a given example"), not a vague feeling — this is what grounds the LLM's gap classification.
- `micro_lesson`: short enough to read in under 20 seconds on camera. If it needs longer, it's not "micro."
- `teach_back_rubric`: 2–4 concrete things the explanation must include — keeps grading grounded and consistent.
