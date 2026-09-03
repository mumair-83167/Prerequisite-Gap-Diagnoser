from pydantic import BaseModel, Field
from typing import Optional, Literal


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded"] = "healthy"
    environment: str
    mock_llm: bool
    model: str


class PlumbingTestRequest(BaseModel):
    code: str = Field(..., description="Python source code executed in Pyodide WASM")
    test_status: Literal["PASS", "FAIL"] = Field(..., description="Execution status from Pyodide")
    error_message: Optional[str] = Field(None, description="Error message if Pyodide test failed")
    execution_time_ms: Optional[float] = Field(None, description="Execution time in milliseconds")


class PlumbingDiagnosticResult(BaseModel):
    status: Literal["acknowledged", "analyzed"] = Field(
        ..., description="Plumbing test acknowledgment status"
    )
    observed_result: Literal["PASS", "FAIL"] = Field(
        ..., description="Observed Pyodide test status"
    )
    diagnostic_echo: str = Field(
        ..., description="Grounded diagnostic message confirming the structured tool call contract"
    )
    is_mock: bool = Field(
        ..., description="Indicates whether this response was generated via deterministic mock or Claude API"
    )
