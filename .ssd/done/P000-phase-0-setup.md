# Proposal P000: Phase 0 — Core Scaffolding & Plumbing

- **Proposal ID:** `P000`
- **Title:** Core Scaffolding, Pyodide WASM Runner & Anthropic Structured Tool-Use Plumbing
- **Status:** `DONE`
- **Phase Mapping:** Phase 0 (Day 1) from [`docs/phases.md`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/docs/phases.md)
- **Primary Agents:** Orchestrator, Research, Architect, Developer, DevOps
- **Target Exit Criteria:** User can submit Python code in the browser, execute it locally via Pyodide WASM with real pass/fail output, and trigger a backend endpoint that returns a structured, validated Claude response.

---

## 1. Governance & Research Dossier

### 1.1 Scope & Boundary Conditions
- **Constraint Checklist:**
  - [x] Client-side code execution ONLY via Pyodide WASM (no backend `eval`, `exec`, or subprocess).
  - [x] Backend API returns strictly typed Pydantic v2 models.
  - [x] LLM calls use Claude Messages API with forced tool-use / structured JSON output (no free-text parsing).
  - [x] Zero secrets committed; `.env` gitignored, `.env.example` provided.
  - [x] Hackathon fast-path: focus on reliable plumbing without premature complexity.

### 1.2 Research Findings: Pyodide WASM in Vite/React
- **Decision:** Adopted the official CDN-based initialization (`https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js`) in `frontend/src/pyodide/runtime.ts`. Verified in-browser execution with real-time stdout/stderr capture and sub-second execution times (~240ms).

### 1.3 Research Findings: Anthropic Structured Output / Tool-Use
- **Pattern:** Forced tool-use schema (`tool_choice={"type": "tool", "name": "diagnostic_result"}`) with Pydantic model validation. Deterministic mock mode supported when `MOCK_LLM=true` or when no API key is set.

### 1.4 Research Findings: Monaco Editor
- `@monaco-editor/react` embedded seamlessly with Python syntax highlighting and dark theme (`vs-dark`).

---

## 2. System Architecture & Components

```
┌────────────────────────────────────────────────────────┐
│  Browser Client (React + Vite + TypeScript)            │
│  ├─ Monaco Code Editor (Python)                        │
│  ├─ Pyodide WASM Sandbox (in-browser execution)        │
│  └─ API Client (typed fetch to FastAPI)                │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP JSON
┌───────────────────────────▼────────────────────────────┐
│  FastAPI Backend (Python 3.12)                         │
│  ├─ CORS Middleware (allowing localhost:5173)          │
│  ├─ /api/health (service status)                       │
│  └─ /api/test-plumbing (validates tool-use output)     │
└───────────────────────────┬────────────────────────────┘
                            │ Anthropic Messages API
┌───────────────────────────▼────────────────────────────┐
│  Claude API (Structured Tool Use)                      │
└────────────────────────────────────────────────────────┘
```

---

## 3. Implementation Cycles & Tasks

### Cycle 0.1: Project Setup & Repo Alignment
- [x] Task 0.1.1: Create [`.env.example`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/.env.example) with environment variable keys.
- [x] Task 0.1.2: Move `copilot-instructions.md` to [`.github/copilot-instructions.md`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/.github/copilot-instructions.md).
- [x] Task 0.1.3: Update [`.gitignore`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/.gitignore) to ensure `.env` and `session_store.sqlite` remain ignored while tracking `.github/` and `.ssd/`.

### Cycle 0.2: Backend Core Scaffolding
- [x] Task 0.2.1: Initialize `backend/` with `requirements.txt` (`fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`, `anthropic`, `python-dotenv`).
- [x] Task 0.2.2: Implement `backend/app/config.py` using `pydantic_settings.BaseSettings`.
- [x] Task 0.2.3: Implement `backend/app/models/schemas.py` with typed request/response models.
- [x] Task 0.2.4: Implement `backend/app/main.py` with FastAPI, CORS middleware, `/api/health`, and `/api/test-plumbing`.

### Cycle 0.3: Frontend Core Scaffolding
- [x] Task 0.3.1: Initialize `frontend/` with Vite (React + TypeScript).
- [x] Task 0.3.2: Install `@monaco-editor/react` and styling utilities.
- [x] Task 0.3.3: Implement typed API client (`frontend/src/api/client.ts`).
- [x] Task 0.3.4: Build basic layout in `frontend/src/App.tsx`.

### Cycle 0.4: Pyodide WASM Runtime Integration
- [x] Task 0.4.1: Add Pyodide CDN script tags to `frontend/index.html`.
- [x] Task 0.4.2: Implement `frontend/src/pyodide/runtime.ts` (singleton WASM loader).
- [x] Task 0.4.3: Implement `frontend/src/pyodide/testRunner.ts` (executes student code against test case assertions).
- [x] Task 0.4.4: Add Monaco Editor & Run Code button in UI with pass/fail banner.

### Cycle 0.5: End-to-End Verification & Phase 0 Exit
- [x] Task 0.5.1: Wire the "Run & Test" button to execute Pyodide client-side.
- [x] Task 0.5.2: Send the execution status to `/api/test-plumbing` and display the structured LLM response in the UI.
- [x] Task 0.5.3: Run automated checks and document Phase 0 completion in `docs/memory.md`.

---

## 4. Verification & Validation Outcomes

1. **Unit & Integration Tests:**
   - Executed `pytest tests/test_plumbing.py` $\rightarrow$ `3 passed in 4.13s` (validated `/api/health`, `PASS` payload validation, and `FAIL` payload validation).
2. **Frontend Production Build:**
   - Executed `npm run build` $\rightarrow$ TypeScript type checking passed with 0 errors; production bundle built cleanly in `dist/`.
3. **End-to-End Browser Flow:**
   - Verified via browser subagent on `http://localhost:5173/`:
     - Pass case executed and confirmed via `Pyodide Test Execution Passed`.
     - Backend diagnostic handshake completed with validated JSON schema.
     - Fail case executed with recursion error and confirmed via `Pyodide Test Execution Failed` and backend acknowledgment.
