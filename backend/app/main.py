import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import anthropic

from app.config import settings
from app.db.init_db import init_db
from app.graph.loader import graph_store
from app.models.schemas import (
    HealthResponse,
    PlumbingTestRequest,
    PlumbingDiagnosticResult,
)
from app.routes import session, submit, diagnose


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite DB and load concept graph
    init_db()
    graph_store.load()
    yield


app = FastAPI(
    title="Prerequisite Gap Diagnoser API",
    description="Backend API powering prerequisite graph traversal and diagnostic reasoning.",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS Middleware to support frontend Vite server on localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Phase 2 Diagnostic Engine Routers
app.include_router(session.router)
app.include_router(submit.router)
app.include_router(diagnose.router)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Service health and environment status endpoint."""
    return HealthResponse(
        status="healthy",
        environment=settings.ENVIRONMENT,
        mock_llm=settings.MOCK_LLM or not bool(settings.ANTHROPIC_API_KEY),
        model=settings.ANTHROPIC_MODEL,
    )


@app.post("/api/test-plumbing", response_model=PlumbingDiagnosticResult)
async def test_plumbing(req: PlumbingTestRequest):
    """Phase 0 verification endpoint (maintained for backwards compatibility)."""
    if settings.MOCK_LLM or not settings.ANTHROPIC_API_KEY:
        if req.test_status == "PASS":
            echo = "Client Pyodide execution verified: Code passed all assertions. Plumbing handshake successful."
        else:
            echo = f"Client Pyodide execution verified: Code failed ({req.error_message or 'Assertion failed'}). Diagnostic engine ready for Phase 2 traversal."

        return PlumbingDiagnosticResult(
            status="acknowledged",
            observed_result=req.test_status,
            diagnostic_echo=echo,
            is_mock=True,
        )

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        tool_definition = {
            "name": "diagnostic_result",
            "description": "Structured schema for returning diagnostic plumbing test feedback.",
            "input_schema": PlumbingDiagnosticResult.model_json_schema(),
        }

        prompt = (
            f"The student submitted the following Python code that executed in client-side Pyodide WASM:\n\n"
            f"```python\n{req.code}\n```\n\n"
            f"Observed test status: {req.test_status}\n"
            f"Error details: {req.error_message or 'None'}\n\n"
            f"Return a structured diagnostic result acknowledging the execution outcome."
        )

        response = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=512,
            tools=[tool_definition],
            tool_choice={"type": "tool", "name": "diagnostic_result"},
            messages=[{"role": "user", "content": prompt}],
        )

        tool_use_block = next((b for b in response.content if b.type == "tool_use"), None)
        if not tool_use_block:
            raise HTTPException(
                status_code=502,
                detail="Anthropic API did not return expected tool_use block",
            )

        data = tool_use_block.input
        data["is_mock"] = False
        return PlumbingDiagnosticResult(**data)

    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal diagnostic error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
