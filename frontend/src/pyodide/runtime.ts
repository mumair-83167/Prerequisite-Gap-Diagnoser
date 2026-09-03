declare global {
  interface Window {
    loadPyodide: (config?: { indexURL?: string }) => Promise<any>;
  }
}

let pyodideInstance: any = null;
let initPromise: Promise<any> | null = null;

export async function getPyodide(): Promise<any> {
  if (pyodideInstance) {
    return pyodideInstance;
  }

  if (initPromise) {
    return initPromise;
  }

  initPromise = (async () => {
    // Wait for the script tag to populate window.loadPyodide if needed
    let retries = 30;
    while (!window.loadPyodide && retries > 0) {
      await new Promise((res) => setTimeout(res, 200));
      retries--;
    }

    if (!window.loadPyodide) {
      throw new Error(
        'Pyodide script failed to load from CDN. Check your internet connection.'
      );
    }

    const pyodide = await window.loadPyodide({
      indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/',
    });

    pyodideInstance = pyodide;
    return pyodide;
  })();

  return initPromise;
}
