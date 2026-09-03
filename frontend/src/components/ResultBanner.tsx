import React from 'react';
import { PyodideRunResult } from '../types';
import { CheckCircle2, XCircle, Clock } from 'lucide-react';

interface ResultBannerProps {
  result: PyodideRunResult | null;
  isRunning: boolean;
}

export const ResultBanner: React.FC<ResultBannerProps> = ({ result, isRunning }) => {
  if (isRunning) {
    return (
      <div className="result-banner result-pass" style={{ background: 'rgba(56, 189, 248, 0.1)', borderColor: 'rgba(56, 189, 248, 0.3)', color: '#38bdf8' }}>
        <div className="result-header">
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="pulse-dot" /> Executing in client-side Pyodide WASM...
          </span>
        </div>
      </div>
    );
  }

  if (!result) return null;

  return (
    <div className={`result-banner ${result.success ? 'result-pass' : 'result-fail'}`}>
      <div className="result-header">
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          {result.success ? (
            <>
              <CheckCircle2 size={16} /> Pyodide Test Execution Passed
            </>
          ) : (
            <>
              <XCircle size={16} /> Pyodide Test Execution Failed
            </>
          )}
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.75rem', opacity: 0.8 }}>
          <Clock size={12} /> {result.executionTimeMs.toFixed(1)} ms
        </span>
      </div>

      {result.error && (
        <div className="result-body" style={{ color: '#fca5a5' }}>
          <strong>Error:</strong> {result.error}
        </div>
      )}

      {result.stdout && (
        <div className="result-body">
          <strong>Stdout:</strong>
          <div>{result.stdout}</div>
        </div>
      )}
    </div>
  );
};
