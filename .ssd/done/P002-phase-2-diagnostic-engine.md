# Proposal P002: Phase 2 — Diagnostic State Machine & Bounded Traversal Engine

- **Proposal ID:** `P002`
- **Title:** Backend Diagnostic State Machine, Bounded Backward BFS, and Grounded Tool-Use Engine
- **Status:** `DONE`
- **Phase Mapping:** Phase 2 (Day 4–7) from [`docs/phases.md`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/docs/phases.md)
- **AI-Team Roles:** Orchestrator (State Invariants & Scope), Architect (State Machine & SQLite Store), AI-ML Specialist (Prompt Grounding & Structured Tool Calls), Developer (BFS & Router Implementation), QA (Traversal, Transition & Full Loop Testing)
- **Project Profile:** `Prototype / hackathon` (Fast-path: depth & polish on recursion demo path, deterministic test harness)

---

## 1. AI-Team Governance & Research Dossier

### 1.1 State Machine Architecture (Architect & Orchestrator)
The diagnostic engine orchestrates learner progression through a formal 7-state finite state machine (FSM):

```
[PRESENT_PROBLEM] ──> Learner views problem
        │
        ▼
 [AWAIT_RESULT]   ──> Learner runs code in client Pyodide WASM
        │
        ├─ (PASS on target problem) ─────────────────────────────────┐
        │                                                            │
        ▼ (FAIL on target problem)                                   │
  [DIAGNOSING]    ──> Backward BFS generates probing questions        │
        │             and classifies gaps                            │
        ▼ (Gap isolated)                                             │
   [TEACHING]     ──> Delivers grounded micro-lesson on gap node     │
        │                                                            │
        ▼                                                            │
  [TEACH_BACK]    ──> Learner explains concept; AI grades rubric     │
        │                                                            │
        ▼ (Rubric passed: understood=True)                           │
   [RE_TEST]      ──> Learner returns to original problem            │
        │                                                            │
        ▼ (PASS on retry)                                            │
   [RESOLVED]     <──────────────────────────────────────────────────┘
```

### 1.2 Bounded Backward BFS Algorithm (Architect & Developer)
- **Root Cause Isolation:** When the learner fails the initial problem at node $T$ (e.g., `recursion`), the engine performs a breadth-first search backward over prerequisite edges:
  $$\text{Queue} = [T], \quad \text{Depth Limit} = 3$$
- Evaluates candidate nodes nearest-first. Skips already mastered nodes. Detects gaps using grounded classification.

### 1.3 Anti-Hallucination & Prompt Grounding Architecture (AI-ML Specialist)
All Claude API interactions strictly use forced tool-use / structured JSON outputs and are grounded in stored node content:
1. **Task 1: Probing Question Generator** — Grounded in `description` and `mastery_signal`.
2. **Task 2: Gap Classifier** — Grounded against stored `mastery_signal` (`gap_detected`, `confidence`, `reasoning`).
3. **Task 3: Teach-Back Grader** — Grounded against stored `teach_back_rubric` checklist (`understood`, `feedback`, `rubric_points_met`).
4. **Security Check:** Node IDs returned by LLM are strictly validated against known graph IDs before driving state transitions (Rule §2).

### 1.4 Database & Persistence (Developer & DevOps)
- SQLite database (`backend/app/db/session_store.sqlite`) storing session progress, traversal history, and node mastery flags.

---

## 2. System Architecture & File Layout

```
backend/app/
  models/
    schemas.py             # Pydantic request/response & tool schemas
    db_models.py           # SQLite table structures
  db/
    init_db.py             # SQLite connection & table initialization
    session_store.sqlite   # Session database (gitignored)
  engine/
    state_machine.py       # Formal 7-state FSM controller
    traversal.py           # Bounded backward BFS algorithm
    llm_calls.py           # Structured tool-use Claude API integration
  prompts/
    probing_question.md    # Versioned prompt template
    gap_classification.md  # Versioned prompt template
    teach_back_grading.md  # Versioned prompt template
  routes/
    session.py             # Start session, fetch problem
    submit.py              # Record Pyodide execution results
    diagnose.py            # Probing questions, answers, micro-lesson, teach-back
tests/
  test_traversal.py        # BFS traversal algorithm tests
  test_llm_calls.py        # Structured tool-use mock & schema tests
  test_state_machine.py    # State machine transition tests
  test_diagnostic_loop.py  # End-to-end diagnostic session verification
```

---

## 3. Implementation Cycles & Task Breakdown

### Cycle 2.1: SQLite Session Store & Diagnostic State Machine Core
- [x] Task 2.1.1: Create [`backend/app/models/db_models.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/models/db_models.py) and [`backend/app/db/init_db.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/db/init_db.py).
- [x] Task 2.1.2: Implement [`backend/app/engine/state_machine.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/engine/state_machine.py) enforcing valid FSM transitions and session persistence.
- [x] Task 2.1.3: Add unit tests in [`backend/tests/test_state_machine.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/tests/test_state_machine.py).

### Cycle 2.2: Bounded Backward BFS Traversal Engine
- [x] Task 2.2.1: Implement [`backend/app/engine/traversal.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/engine/traversal.py) with bounded BFS ($\le 3$ hops), visited deduplication, and topological ordering.
- [x] Task 2.2.2: Add unit tests in [`backend/tests/test_traversal.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/tests/test_traversal.py).

### Cycle 2.3: Grounded Prompts & Structured Tool-Use Engine
- [x] Task 2.3.1: Author versioned prompt templates in [`backend/app/prompts/`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/prompts/).
- [x] Task 2.3.2: Implement [`backend/app/engine/llm_calls.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/engine/llm_calls.py) with forced tool schemas and deterministic offline mock fallbacks.
- [x] Task 2.3.3: Add unit tests in [`backend/tests/test_llm_calls.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/tests/test_llm_calls.py).

### Cycle 2.4: FastAPI Diagnostic API Routers
- [x] Task 2.4.1: Implement session router [`backend/app/routes/session.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/routes/session.py).
- [x] Task 2.4.2: Implement submission router [`backend/app/routes/submit.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/routes/submit.py).
- [x] Task 2.4.3: Implement diagnostic router [`backend/app/routes/diagnose.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/routes/diagnose.py).
- [x] Task 2.4.4: Mount all routers in [`backend/app/main.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/app/main.py).

### Cycle 2.5: Automated Verification & Full-Loop Test Harness
- [x] Task 2.5.1: Build end-to-end integration test [`backend/tests/test_diagnostic_loop.py`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/backend/tests/test_diagnostic_loop.py) verifying the complete diagnostic cycle on the recursion path.
- [x] Task 2.5.2: Execute `pytest` across all test modules to verify 100% test pass (22/22 passed).
- [x] Task 2.5.3: Archive proposal to `.ssd/done/` and log Phase 2 completion in `docs/memory.md`.

---

## 4. Exit Criteria & Validation Outcomes

1. **State Machine Integrity:** All transitions between `PRESENT_PROBLEM` and `RESOLVED` are strictly validated; invalid transitions raise `InvalidStateTransitionError`.
2. **Bounded BFS Correctness:** Backward traversal never exceeds depth 3 and correctly yields candidate prerequisites nearest-first.
3. **Structured Tool-Use Validation:** All 3 LLM calls return validated JSON conforming to Pydantic schemas, with verified mock fallback.
4. **End-to-End Loop Verified:** Integration test simulates the entire loop (`fail code` $\rightarrow$ `probing question` $\rightarrow$ `diagnose gap` $\rightarrow$ `micro-lesson` $\rightarrow$ `teach-back` $\rightarrow$ `re-test pass`) and confirms state progression to `RESOLVED`.
