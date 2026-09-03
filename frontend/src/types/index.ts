export interface HealthResponse {
  status: 'healthy' | 'degraded';
  environment: string;
  mock_llm: boolean;
  model: string;
}

export interface PlumbingTestRequest {
  code: string;
  test_status: 'PASS' | 'FAIL';
  error_message?: string | null;
  execution_time_ms?: number | null;
}

export interface PlumbingDiagnosticResult {
  status: 'acknowledged' | 'analyzed';
  observed_result: 'PASS' | 'FAIL';
  diagnostic_echo: string;
  is_mock: boolean;
}

export interface PyodideRunResult {
  success: boolean;
  stdout: string;
  stderr: string;
  error?: string;
  executionTimeMs: number;
}
