import { getPyodide } from './runtime';
import { PyodideRunResult } from '../types';

/**
 * Executes student Python code against a test harness inside client-side Pyodide WASM.
 * No server execution occurs.
 */
export async function runStudentCode(
  studentCode: string,
  testHarness: string
): Promise<PyodideRunResult> {
  const pyodide = await getPyodide();

  // Harness setup to redirect stdout and stderr
  const setupCode = `
import sys
import io
sys_stdout = io.StringIO()
sys_stderr = io.StringIO()
sys.stdout = sys_stdout
sys.stderr = sys_stderr
`;

  const teardownCode = `
_captured_stdout = sys_stdout.getvalue()
_captured_stderr = sys_stderr.getvalue()
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
`;

  const fullProgram = `${setupCode}\n${studentCode}\n${testHarness}\n${teardownCode}`;

  const startTime = performance.now();
  let stdout = '';
  let stderr = '';

  try {
    await pyodide.runPythonAsync(fullProgram);
    stdout = pyodide.globals.get('_captured_stdout') || '';
    stderr = pyodide.globals.get('_captured_stderr') || '';
    const executionTimeMs = performance.now() - startTime;

    return {
      success: true,
      stdout,
      stderr,
      executionTimeMs,
    };
  } catch (err: any) {
    const executionTimeMs = performance.now() - startTime;
    // Attempt to salvage any stdout printed before error
    try {
      stdout = pyodide.globals.get('_captured_stdout') || '';
      stderr = pyodide.globals.get('_captured_stderr') || '';
    } catch {
      // Ignore if globals aren't accessible
    }

    const rawError = err.message || String(err);
    // Clean up python traceback to isolate the message
    const errorLines = rawError.split('\n');
    const cleanError = errorLines.slice(-2).join(' ').trim() || rawError;

    return {
      success: false,
      stdout,
      stderr: stderr || rawError,
      error: cleanError,
      executionTimeMs,
    };
  }
}
