# Proposal P000: Phase 0 — Core Scaffolding & Plumbing

- **Proposal ID:** `P000`
- **Title:** Core Scaffolding, Pyodide WASM Runner & Anthropic Structured Tool-Use Plumbing
- **Status:** `ACTIVE`
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
- **Evaluation: CDN vs. NPM Bundle:**
  - *NPM bundle (`pyodide` package)* requires Vite to bundle large `.wasm` and `.data` binaries, leading to tricky MIME-type issues, Web Worker configuration overhead, and heavy bundle bloat.
  - *CDN script loader (`https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js`)* loads the official Pyodide runtime asynchronously on demand. It is battle-tested, isolated, and standard for browser-based Python runners.
  - *Decision:* Adopt the CDN-based initialization in `frontend/src/pyodide/runtime.ts`.

### 1.3 Research Findings: Anthropic Structured Output / Tool-Use
- **Pattern:** Using the Anthropic Messages API (`anthropic` Python SDK):
  ```python
  client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
  response = await client.messages.create(
      model="claude-3-5-sonnet-20241022",
      max_tokens=512,
      tools=[{
          "name": "ping_plumbing_test",
          "description": "Plumbing test schema for Phase 0 verification",
          "input_schema": PingResponseSchema.model_json_schema()
      }],
      tool_choice={"type": "tool", "name": "ping_plumbing_test"},
      messages=[{"role": "user", "content": prompt}]
  )
  ```
- *Fallback for dev without active API key:* A deterministic mock flag (`MOCK_LLM=true`) will be supported in `config.py` so local frontend and backend plumbing can be tested offline without failing.

### 1.4 Research Findings: Monaco Editor
- `@monaco-editor/react` provides full VS Code editing ergonomics with Python syntax highlighting and dark theme, mounting smoothly in React 18 / 19 with zero webpack/vite worker configuration.

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
- [ ] Task 0.1.1: Create [`.env.example`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/.env.example) with environment variable keys.
- [ ] Task 0.1.2: Move `copilot-instructions.md` to [`.github/copilot-instructions.md`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/.github/copilot-instructions.md).
- [ ] Task 0.1.3: Update [`.gitignore`](file:///d:/Projects/Prerequisite-Gap-Diagnoser/.gitignore) to ensure `.env` and `session_store.sqlite` remain ignored while tracking `.github/` and `.ssd/`.

### Cycle 0.2: Backend Core Scaffolding
- [ ] Task 0.2.1: Initialize `backend/` with `requirements.txt` (`fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`, `anthropic`, `python-dotenv`).
- [ ] Task 0.2.2: Implement `backend/app/config.py` using `pydantic_settings.BaseSettings`.
- [ ] Task 0.2.3: Implement `backend/app/models/schemas.py` with typed request/response models.
- [ ] Task 0.2.4: Implement `backend/app/main.py` with FastAPI, CORS middleware, `/api/health`, and `/api/test-plumbing`.

### Cycle 0.3: Frontend Core Scaffolding
- [ ] Task 0.3.1: Initialize `frontend/` with Vite (React + TypeScript).
- [ ] Task 0.3.2: Install `@monaco-editor/react` and styling utilities.
- [ ] Task 0.3.3: Implement typed API client (`frontend/src/api/client.ts`).
- [ ] Task 0.3.4: Build basic layout in `frontend/src/App.tsx`.

### Cycle 0.4: Pyodide WASM Runtime Integration
- [ ] Task 0.4.1: Add Pyodide CDN script tags to `frontend/index.html`.
- [ ] Task 0.4.2: Implement `frontend/src/pyodide/runtime.ts` (singleton WASM loader).
- [ ] Task 0.4.3: Implement `frontend/src/pyodide/testRunner.ts` (executes student code against test case assertions).
- [ ] Task 0.4.4: Add Monaco Editor & Run Code button in UI with pass/fail banner.

### Cycle 0.5: End-to-End Verification & Phase 0 Exit
- [ ] Task 0.5.1: Wire the "Run & Test" button to execute Pyodide client-side.
- [ ] Task 0.5.2: Send the execution status to `/api/test-plumbing` and display the structured LLM response in the UI.
- [ ] Task 0.5.3: Run automated checks and document Phase 0 completion in `docs/memory.md`.

---

## 4. Exit Criteria & Verification Method

1. **Client-Side WASM Execution:** Submitting a correct Python function returns `PASS`; submitting an erroneous function returns `FAIL` with trace info, with zero network calls to the backend for execution.
2. **Backend Structured Response:** Calling `/api/test-plumbing` returns HTTP 200 with validated JSON conforming to the Pydantic schema.
3. **End-to-End User Flow:** Clicking "Test End-to-End Flow" runs the code in Pyodide, pings the backend, and presents the combined results on screen.
