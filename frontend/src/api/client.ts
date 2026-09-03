import { HealthResponse, PlumbingTestRequest, PlumbingDiagnosticResult } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: HTTP ${res.status}`);
  }
  return res.json();
}

export async function sendPlumbingTest(
  payload: PlumbingTestRequest
): Promise<PlumbingDiagnosticResult> {
  const res = await fetch(`${API_BASE_URL}/api/test-plumbing`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`Plumbing test failed [HTTP ${res.status}]: ${errorBody}`);
  }

  return res.json();
}
