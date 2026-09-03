import React, { useState, useEffect } from 'react';
import { CodeEditor } from './components/CodeEditor';
import { ResultBanner } from './components/ResultBanner';
import { runStudentCode } from './pyodide/testRunner';
import { getPyodide } from './pyodide/runtime';
import { fetchHealth, sendPlumbingTest } from './api/client';
import { HealthResponse, PyodideRunResult, PlumbingDiagnosticResult } from './types';
import { Play, RotateCcw, Server, Cpu, Sparkles, AlertTriangle, CheckCircle } from 'lucide-react';

const PASSING_CODE = `def factorial(n):
    # Correct recursive solution
    if n <= 1:
        return 1
    return n * factorial(n - 1)
`;

const FAILING_CODE = `def factorial(n):
    # Buggy recursive solution (missing base case condition causing infinite recursion)
    return n * factorial(n - 1)
`;

const TEST_HARNESS = `
# Hidden verification test cases
assert factorial(1) == 1, "factorial(1) should be 1"
assert factorial(5) == 120, "factorial(5) should be 120"
assert factorial(0) == 1, "factorial(0) should be 1"
print("All test assertions passed successfully!")
`;

export const App: React.FC = () => {
  const [code, setCode] = useState<string>(PASSING_CODE);
  const [pyodideReady, setPyodideReady] = useState<boolean>(false);
  const [pyodideLoadingError, setPyodideLoadingError] = useState<string | null>(null);
  const [backendHealth, setBackendHealth] = useState<HealthResponse | null>(null);

  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [pyodideResult, setPyodideResult] = useState<PyodideRunResult | null>(null);

  const [isDiagnosing, setIsDiagnosing] = useState<boolean>(false);
  const [diagnosticResult, setDiagnosticResult] = useState<PlumbingDiagnosticResult | null>(null);
  const [diagnosticError, setDiagnosticError] = useState<string | null>(null);

  // Initialize Pyodide WASM and ping backend on mount
  useEffect(() => {
    // Init Pyodide
    getPyodide()
      .then(() => setPyodideReady(true))
      .catch((err) => {
        console.error('Pyodide init error:', err);
        setPyodideLoadingError(err.message || 'Failed to initialize Pyodide WASM');
      });

    // Check backend health
    fetchHealth()
      .then((health) => setBackendHealth(health))
      .catch((err) => {
        console.warn('Backend currently unreachable:', err.message);
      });
  }, []);

  const handleRunCode = async () => {
    if (!code) return;
    setIsRunning(true);
    setPyodideResult(null);

    const result = await runStudentCode(code, TEST_HARNESS);
    setPyodideResult(result);
    setIsRunning(false);

    // Automatically trigger backend diagnostic plumbing test to complete Phase 0 exit loop
    await handleSendToBackend(result);
  };

  const handleSendToBackend = async (runRes: PyodideRunResult) => {
    setIsDiagnosing(true);
    setDiagnosticError(null);
    try {
      const resp = await sendPlumbingTest({
        code,
        test_status: runRes.success ? 'PASS' : 'FAIL',
        error_message: runRes.error || null,
        execution_time_ms: runRes.executionTimeMs,
      });
      setDiagnosticResult(resp);
    } catch (err: any) {
      console.error('Backend diagnostic call failed:', err);
      setDiagnosticError(err.message || 'Diagnostic backend request failed');
    } finally {
      setIsDiagnosing(false);
    }
  };

  return (
    <div className="app-layout">
      {/* Header */}
      <header className="app-header">
        <div className="brand-container">
          <div className="brand-icon">PG</div>
          <div>
            <div className="brand-title">Prerequisite Gap Diagnoser</div>
            <div className="brand-subtitle">AI-Guided Misconception Tracing for CS Students</div>
          </div>
        </div>

        <div className="status-badges">
          {/* Pyodide Badge */}
          {pyodideReady ? (
            <span className="badge badge-green">
              <Cpu size={12} /> Pyodide WASM Ready
            </span>
          ) : pyodideLoadingError ? (
            <span className="badge badge-coral" style={{ color: '#f43f5e' }}>
              <AlertTriangle size={12} /> Pyodide Error
            </span>
          ) : (
            <span className="badge badge-amber">
              <span className="pulse-dot" /> Initializing Pyodide...
            </span>
          )}

          {/* Backend Status Badge */}
          {backendHealth ? (
            <span className="badge badge-blue">
              <Server size={12} /> API Connected ({backendHealth.mock_llm ? 'Mock LLM' : backendHealth.model})
            </span>
          ) : (
            <span className="badge badge-amber">
              <Server size={12} /> API Disconnected
            </span>
          )}
        </div>
      </header>

      {/* Main Container */}
      <main className="main-container">
        {/* Phase 0 Banner */}
        <div className="phase-banner">
          <div>
            <h2>Phase 0 — Core Scaffolding & Plumbing Active</h2>
            <p>
              Testing the end-to-end loop: Client-side Python execution in Pyodide WASM $\rightarrow$ Structured Claude API Diagnostic Call.
            </p>
          </div>
          <span className="badge badge-blue" style={{ padding: '0.4rem 0.8rem' }}>
            Phase 0 / Day 1
          </span>
        </div>

        {/* 2-Column Grid */}
        <div className="grid-container">
          {/* Left Column: Monaco Code Editor & Pyodide Runner */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">
                <Cpu size={16} color="#38bdf8" /> Python Problem: Recursive Factorial
              </span>
              <div className="button-row">
                <button
                  className="btn btn-secondary"
                  onClick={() => setCode(PASSING_CODE)}
                  disabled={isRunning}
                  style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
                >
                  Load Pass Case
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => setCode(FAILING_CODE)}
                  disabled={isRunning}
                  style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
                >
                  Load Fail Case
                </button>
              </div>
            </div>

            <div className="card-body">
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Write a function <code>factorial(n)</code> that returns the product of all positive integers $\le n$.
              </div>

              {/* Monaco Code Editor */}
              <CodeEditor
                value={code}
                onChange={(val) => setCode(val || '')}
              />

              {/* Action Buttons */}
              <div className="button-row">
                <button
                  className="btn btn-primary"
                  onClick={handleRunCode}
                  disabled={!pyodideReady || isRunning}
                >
                  <Play size={15} />
                  {isRunning ? 'Running in WASM...' : 'Run in Pyodide WASM & Test'}
                </button>

                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    setCode(PASSING_CODE);
                    setPyodideResult(null);
                    setDiagnosticResult(null);
                  }}
                  disabled={isRunning}
                >
                  <RotateCcw size={15} /> Reset
                </button>
              </div>

              {/* Result Banner */}
              <ResultBanner result={pyodideResult} isRunning={isRunning} />
            </div>
          </div>

          {/* Right Column: Diagnostic Plumbing & Structured Response */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">
                <Sparkles size={16} color="#a855f7" /> Backend Diagnostic Plumbing
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Structured Claude API Tool-Use
              </span>
            </div>

            <div className="card-body diagnostic-panel">
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Validates the contract between client execution and the backend diagnostic engine using strict Pydantic schemas.
              </p>

              {isDiagnosing && (
                <div className="diagnostic-box" style={{ borderColor: 'rgba(168, 85, 247, 0.4)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#c084fc', fontSize: '0.85rem' }}>
                    <span className="pulse-dot" /> Awaiting structured response from backend...
                  </div>
                </div>
              )}

              {diagnosticError && (
                <div className="diagnostic-box" style={{ borderColor: 'rgba(244, 63, 94, 0.4)', background: 'rgba(244, 63, 94, 0.05)' }}>
                  <div className="diagnostic-label" style={{ color: '#f43f5e' }}>Error Encountered</div>
                  <div className="diagnostic-text" style={{ color: '#fda4af' }}>{diagnosticError}</div>
                </div>
              )}

              {diagnosticResult && (
                <div className="diagnostic-box" style={{ borderColor: 'rgba(34, 197, 94, 0.4)', background: 'rgba(34, 197, 94, 0.04)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span className="diagnostic-label">Status: {diagnosticResult.status}</span>
                    <span className="badge badge-green" style={{ fontSize: '0.7rem' }}>
                      <CheckCircle size={10} /> Validated JSON Schema
                    </span>
                  </div>

                  <div className="diagnostic-text">
                    {diagnosticResult.diagnostic_echo}
                  </div>

                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                    <span className="badge badge-blue">
                      Observed: {diagnosticResult.observed_result}
                    </span>
                    <span className="badge badge-purple" style={{ background: 'rgba(168, 85, 247, 0.1)', color: '#c084fc', borderColor: 'rgba(168, 85, 247, 0.3)' }}>
                      Engine: {diagnosticResult.is_mock ? 'Mock Plumbing' : 'Anthropic Claude'}
                    </span>
                  </div>
                </div>
              )}

              {/* Hidden Test Case Definition */}
              <div className="diagnostic-box">
                <div className="diagnostic-label">Active Test Suite (Pyodide Assertion Block)</div>
                <div className="log-terminal">
                  {TEST_HARNESS.trim()}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
