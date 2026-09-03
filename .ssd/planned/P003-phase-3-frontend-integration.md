# Proposal P003: Phase 3 — Frontend UI & Graph Traversal Animation

- **Status:** `PLANNED`
- **Target Phase:** Phase 3 (Day 8–11)
- **Primary Owner:** Frontend Developer / UX Designer
- **Dependencies:** P002 (Diagnostic Engine)

---

## 1. Objectives
- Implement 3-zone unified UI (Monaco Editor, Graph Visualizer, Dynamic Diagnostic Panel).
- Build the concept graph interactive visualizer using React Flow with custom state-colored nodes:
  `Gray` (untested) $\rightarrow$ `Amber` (probing) $\rightarrow$ `Coral` (gap) $\rightarrow$ `Teal` (mastered).
- Wire Monaco code editor to client-side Pyodide execution with instant pass/fail feedback.
- Connect interactive panel to backend diagnostic loop (questions $\rightarrow$ micro-lesson $\rightarrow$ teach-back input).

---

## 2. Planned Cycles
- **Cycle 3.1:** Monaco Editor & Pyodide Test Suite UI.
- **Cycle 3.2:** React Flow Concept Graph & Animated Traversal Hooks.
- **Cycle 3.3:** Dynamic Diagnostic / Teach-Back Panel.
- **Cycle 3.4:** End-to-End User Flow Integration on Recursion Demo Path.
