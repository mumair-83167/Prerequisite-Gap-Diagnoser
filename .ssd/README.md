# System Solution Delivery (.ssd) Governance & Proposal Framework

The `.ssd` directory manages the formal proposals, engineering cycles, and task governance for the **Prerequisite Gap Diagnoser** project, operating in synergy with `.ai-team` guidelines and canonical project documentation (`AGENTS.md`, `docs/`).

---

## 1. Directory Structure

```
.ssd/
├── README.md               # Governance rules, workflow lifecycle, and lifecycle stages
├── active/                 # The single active proposal currently in execution
│   └── P000-phase-0-setup.md
├── planned/                # Scheduled proposals for subsequent phases
│   ├── P001-phase-1-content-graph.md
│   ├── P002-phase-2-diagnostic-engine.md
│   ├── P003-phase-3-frontend-integration.md
│   ├── P004-phase-4-polish-robustness.md
│   └── P005-phase-5-demo-submission.md
└── done/                   # Fully implemented, tested, and accepted proposals
```

---

## 2. Proposal Lifecycle & States

1. **Planned (`planned/`):**
   - High-level scope, objectives, and prerequisites identified based on `docs/phases.md`.
   - Architectural guardrails aligned with `docs/rules.md`.

2. **Active (`active/`):**
   - Activated by the Orchestrator when work begins.
   - Requires completing the **Governance Research Workflow** before code implementation.
   - Broken down into discrete, sequenced **Cycles** and actionable **Tasks**.
   - Contains live execution logs and test verification records.

3. **Done (`done/`):**
   - Transitioned only after the phase **Exit Criteria** and Definition of Done (`.ai-team/shared-rules.md` §12) are fully met.
   - `docs/memory.md` is updated with decisions made, lessons learned, and phase completion.

---

## 3. Governance Research Workflow (Before Implementation)

Before code is written for any active proposal, the team executes the following governance protocol:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Problem & Scope Analysis (Orchestrator)                  │
│    - Confirm boundary conditions from docs/rules.md         │
│    - Validate against 2-minute demo payoff & hackathon time │
├─────────────────────────────────────────────────────────────┤
│ 2. Deep Technical Research (Research Agent)                 │
│    - Check library currency, compatibility & known issues   │
│    - Verify API contracts & zero-sandbox constraints        │
├─────────────────────────────────────────────────────────────┤
│ 3. Solution Specification & Architecture (Architect)       │
│    - Define data models, schemas, and endpoints             │
│    - Sequence work into verifiable Cycles (0.1, 0.2, etc.)  │
├─────────────────────────────────────────────────────────────┤
│ 4. Proposal Approval & Task Assignment (Orchestrator)       │
│    - Review against Definition of Done                      │
│    - Authorize implementation cycles                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Proposal Template Standards

Every proposal in `.ssd/` adheres to a strict schema:
- **Proposal ID & Title:** e.g., `P000: Phase 0 — Core Scaffolding & Plumbing`
- **Status:** `PLANNED` | `ACTIVE` | `DONE`
- **Parent Phase & Deadline:** Mapped to `docs/phases.md`
- **Research Dossier:** Technical investigation, choices made, rejected alternatives
- **System Architecture Impact:** Endpoints, schema changes, state changes
- **Implementation Cycles:** Sequenced delivery milestones
- **Task Checklist:** Granular items marked `[ ]` or `[x]`
- **Verification & Exit Criteria:** Concrete verification commands and criteria
