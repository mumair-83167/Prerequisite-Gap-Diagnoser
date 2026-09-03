# Proposal P001: Phase 1 — Content Authoring & Concept Graph Freezing

- **Status:** `PLANNED`
- **Target Phase:** Phase 1 (Day 2–3)
- **Primary Owner:** AI-ML / Education Content Author
- **Dependencies:** P000 (Scaffold & Plumbing)

---

## 1. Objectives
- Author the complete 20–25 node Python fundamentals concept graph (`concept_graph.json`).
- Provide rich metadata for the recursion demo path:
  `recursion` → `functions` → `conditionals` (with base cases, call stacks, return values).
- Grounding assets per demo node: `description`, `mastery_signal`, `micro_lesson`, `teach_back_rubric`, and test-case-backed `sample_problem`.
- **Freeze** graph JSON permanently upon completion (Rule §1: no mid-build node additions).

---

## 2. Planned Cycles
- **Cycle 1.1:** Graph Schema & Validation Script (`scripts/seed_graph.py`).
- **Cycle 1.2:** Demo Path Deep Content (Recursion, Functions, Conditionals, Scope).
- **Cycle 1.3:** Peripheral Graph Nodes (Variables, Loops, Lists, Operators) for realistic graph rendering.
- **Cycle 1.4:** Graph Freeze Review & Pydantic validation test suite.
