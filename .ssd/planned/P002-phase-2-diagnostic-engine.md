# Proposal P002: Phase 2 — Diagnostic State Machine & Bounded Traversal Engine

- **Status:** `PLANNED`
- **Target Phase:** Phase 2 (Day 4–7)
- **Primary Owner:** Backend Developer / AI-ML Specialist
- **Dependencies:** P001 (Frozen Concept Graph)

---

## 1. Objectives
- Implement backend diagnostic state machine:
  `PRESENT_PROBLEM → AWAIT_RESULT → DIAGNOSING → TEACHING → TEACH_BACK → RE_TEST → RESOLVED`.
- Implement bounded backward BFS algorithm (depth $\le 3$) over prerequisites.
- Integrate the 3 structured Claude API tool-use calls:
  1. Diagnostic probing question generator
  2. Gap classifier (grounded against `mastery_signal`)
  3. Teach-back grader (grounded against `teach_back_rubric`)
- Enforce strict node ID validation against known graph nodes.

---

## 2. Planned Cycles
- **Cycle 2.1:** State Machine Model & SQLite Session Store.
- **Cycle 2.2:** Graph Traversal Logic (Bounded BFS with cycle prevention).
- **Cycle 2.3:** LLM Grounded Tool-Use Calls with Schema Validation.
- **Cycle 2.4:** CLI / Automated Test Harness verifying the full diagnostic loop on the recursion path.
