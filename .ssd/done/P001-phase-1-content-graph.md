# Proposal P001: Phase 1 — Content Authoring & Concept Graph Freezing

- **Proposal ID:** `P001`
- **Title:** Authoring, Validating, and Freezing the 20–22 Node Python Fundamentals Concept Graph
- **Status:** `DONE`
- **Phase Mapping:** Phase 1 (Day 2–3) from [`docs/phases.md`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/docs/phases.md)
- **AI-Team Roles:** Orchestrator (Scope & Freeze), Research & AI-ML (Pedagogy & Grounding Rubrics), Architect (DAG Invariants & Schema), Developer (Loader & CLI Validator), QA (Acyclicity & Invariant Testing)
- **Project Profile:** `Prototype / hackathon` (Fast-path: depth & polish on the 1 demo path, clean peripheral nodes for realistic graph visualization)

---

## 1. AI-Team Governance & Research Dossier

### 1.1 Scope Boundaries & Freeze Contract (Orchestrator)
- **Hard Rule (§1):** The node list is **FROZEN** upon completion of this proposal. No nodes will be added or restructured mid-build during Phases 2, 3, or 4.
- **Node Count:** Exactly 21 nodes (Target: 20–22).
- **Target Demo Path:**
  $$\text{recursion} \longrightarrow \text{call\_stack} \longrightarrow \text{functions} \longrightarrow \text{conditionals} \longrightarrow \text{comparison\_operators}$$
- When a student fails recursive factorial due to missing or faulty termination logic, the diagnostic engine traverses backward to pinpoint either **conditionals** or **call_stack/base_case** as the true upstream prerequisite gap.

### 1.2 Anti-Hallucination & Grounding Rubrics (Research & AI-ML)
Every node in the concept graph contains explicit ground-truth metadata that bounds all future Claude API calls:
1. `mastery_signal`: Concrete observable behavior that the diagnostic classifier tests against (e.g. *"Can differentiate the base termination condition from the recursive progression"*), preventing the LLM from using unguided opinions.
2. `micro_lesson`: A short, highly readable explanation with code snippet, designed to be read in $<20$ seconds on screen.
3. `teach_back_rubric`: 2–4 mandatory conceptual items required in student teach-back explanations.
4. `sample_problem`: Python problem prompt, starter code, and assertion-backed test harness for client-side Pyodide execution.

### 1.3 Graph Topology & Pedagogical Hierarchy (Architect)
The concept graph is organized into 6 pedagogical tiers:
- **Tier 0 (Primitives):** `variables`, `data_types`, `arithmetic_operators` (3 nodes)
- **Tier 1 (Logic & Ops):** `comparison_operators`, `boolean_logic` (2 nodes)
- **Tier 2 (Control Flow):** `conditionals`, `loops_while`, `loops_for` (3 nodes)
- **Tier 3 (State & Scope):** `lists`, `indexing_slicing`, `variable_scope` (3 nodes)
- **Tier 4 (Functions & Stack Mechanics):** `functions`, `function_parameters`, `return_values`, `call_stack` (4 nodes)
- **Tier 5 (Recursion Primitives & Extensions):** `base_case`, `recursive_step`, `recursion`, `tree_recursion`, `accumulator_pattern`, `recursive_trace` (6 nodes)

### 1.4 Graph Mathematical Invariants (QA & Architect)
1. **DAG Property:** Strictly acyclic ($G = (V, E)$ has no directed cycles).
2. **Referential Integrity:** 100% of prerequisite IDs resolve to existing nodes.
3. **Bounded Traversal Invariant:** The shortest prerequisite distance from `recursion` to `conditionals` is 2 hops (via `base_case`), satisfying the bounded BFS constraint ($\le 3$).

---

## 2. System Architecture & File Layout

```
backend/
  app/
    models/
      schemas.py             # ConceptNode, SampleProblem, ConceptGraph Pydantic models
    graph/
      __init__.py
      concept_graph.json     # The frozen 21-node JSON document
      loader.py              # Startup loader, DAG acyclicity validation & node index
  tests/
    test_graph_loader.py     # Automated tests: schema, referential integrity & DAG invariants
scripts/
  seed_graph.py              # CLI validation & inspection tool
```

---

## 3. Implementation Cycles & Task Breakdown

### Cycle 1.1: Graph Schema Specification & Validation Engine
- [x] Task 1.1.1: Add `SampleProblem`, `ConceptNode`, and `ConceptGraph` Pydantic models to [`backend/app/models/schemas.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/models/schemas.py).
- [x] Task 1.1.2: Implement [`backend/app/graph/loader.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/graph/loader.py) with cycle detection (topological sort/DFS), prerequisite validation, and memoized graph access.
- [x] Task 1.1.3: Implement CLI validator [`scripts/seed_graph.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/scripts/seed_graph.py) that reports node count, edge count, demo path depth, and checks for DAG validity.

### Cycle 1.2: Deep Content Authoring for Demo Path Nodes
- [x] Task 1.2.1: Author `recursion` node (target problem: recursive factorial, rich test harness).
- [x] Task 1.2.2: Author `base_case` & `recursive_step` nodes (grounded mastery signals & micro-lessons).
- [x] Task 1.2.3: Author `call_stack` & `functions` nodes (frame mechanics, return flow).
- [x] Task 1.2.4: Author `return_values` & `conditionals` nodes (the pivotal root cause gap for the demo).
- [x] Task 1.2.5: Author `comparison_operators` node (equality and relational checks).

### Cycle 1.3: Peripheral Graph Node Authoring (Complete 20–22 Node DAG)
- [x] Task 1.3.1: Author Tier 0 primitives (`variables`, `data_types`, `arithmetic_operators`).
- [x] Task 1.3.2: Author Tier 1 logic (`boolean_logic`).
- [x] Task 1.3.3: Author Tier 2 & 3 constructs (`loops_while`, `loops_for`, `lists`, `indexing_slicing`, `variable_scope`, `function_parameters`).
- [x] Task 1.3.4: Assemble complete [`backend/app/graph/concept_graph.json`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/graph/concept_graph.json).

### Cycle 1.4: Integrity Verification & Formal Graph Freeze
- [x] Task 1.4.1: Create automated test suite [`backend/tests/test_graph_loader.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/tests/test_graph_loader.py).
- [x] Task 1.4.2: Execute `pytest tests/test_graph_loader.py` and `python scripts/seed_graph.py`.
- [x] Task 1.4.3: Verify backward BFS traversal reaches root cause in $\le 3$ hops.
- [x] Task 1.4.4: Archive proposal to `.ssd/done/` and log graph freeze in `docs/memory.md`.

---

## 4. Exit Criteria & Validation Outcomes

1. **Schema Adherence:** `concept_graph.json` parses with 0 validation errors against Pydantic models.
2. **DAG Integrity:** Strict acyclicity confirmed (0 cycles, 0 circular dependencies).
3. **Referential Integrity:** 100% of 28 prerequisite links resolve cleanly.
4. **Demo Path Completeness:** Every node on the demo path contains non-empty `description`, `mastery_signal`, `micro_lesson`, `teach_back_rubric`, and test-backed `sample_problem`.
5. **Graph Freeze:** `concept_graph.json` is formally locked and frozen for Phase 2 and beyond.
