from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any


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


# ── Concept Graph Data Models (Phase 1) ───────────────────────────────────

class SampleProblem(BaseModel):
    id: str = Field(..., description="Unique problem identifier")
    title: str = Field(..., description="Human-readable problem title")
    prompt: str = Field(..., description="Problem description and instructions")
    starter_code: str = Field(..., description="Initial starter code for the learner")
    test_harness: str = Field(..., description="Hidden Python test assertions executed in Pyodide")


class ConceptNode(BaseModel):
    id: str = Field(..., description="Unique snake_case concept identifier (e.g. 'recursion')")
    name: str = Field(..., description="Display name of the concept (e.g. 'Recursion')")
    tier: int = Field(..., ge=0, le=5, description="Hierarchical tier (0=Primitives, 5=Target/Advanced)")
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Direct upstream prerequisite node IDs in the DAG"
    )
    description: str = Field(
        ..., description="Plain-language 1-2 sentence definition of the concept"
    )
    mastery_signal: str = Field(
        ..., description="Observable competence signal used to ground LLM gap classification"
    )
    micro_lesson: str = Field(
        ..., description="Concise explanation and code example readable in <20 seconds"
    )
    teach_back_rubric: List[str] = Field(
        ..., min_length=2, max_length=5,
        description="2-4 concrete criteria required in learner teach-back explanations"
    )
    sample_problem: Optional[SampleProblem] = Field(
        None, description="Associated Python exercise backed by Pyodide test harness"
    )


class ConceptGraph(BaseModel):
    version: str = Field(..., description="Concept graph version string")
    domain: str = Field(default="python_fundamentals", description="Educational domain")
    target_node_id: str = Field(default="recursion", description="Primary demo exercise node ID")
    demo_path: List[str] = Field(
        default_factory=list,
        description="The primary scripted traversal path for video demonstrations"
    )
    nodes: List[ConceptNode] = Field(..., description="List of all concept nodes in the graph")


# ── Diagnostic Engine Schemas (Phase 2) ───────────────────────────────────

class ProbingQuestionResult(BaseModel):
    concept_id: str = Field(..., description="Node ID being probed")
    question: str = Field(..., description="Focused diagnostic question testing mastery signal")
    is_mock: bool = Field(default=False)


class ProbingAnswerRequest(BaseModel):
    answer: str = Field(..., description="Learner's response to the probing question")


class GapClassificationResult(BaseModel):
    concept_id: str = Field(..., description="Node ID evaluated")
    gap_detected: bool = Field(..., description="True if student has a gap on this prerequisite")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(..., description="Pedagogical justification grounded in mastery signal")
    is_mock: bool = Field(default=False)


class TeachBackRequest(BaseModel):
    explanation: str = Field(..., description="Learner's explanation of the concept in their own words")


class TeachBackGradingResult(BaseModel):
    concept_id: str = Field(..., description="Node ID taught")
    understood: bool = Field(..., description="True if explanation meets rubric criteria")
    feedback: str = Field(..., description="Constructive pedagogical feedback")
    rubric_points_met: List[str] = Field(default_factory=list, description="List of rubric criteria met")
    is_mock: bool = Field(default=False)


class SessionStateResponse(BaseModel):
    session_id: str
    state: str
    target_node_id: str
    diagnosed_gap_node_id: Optional[str] = None
    current_candidate_node_id: Optional[str] = None
    probing_question: Optional[str] = None
    traversal_path: List[str]
    mastered_nodes: List[str]
    problem: Optional[SampleProblem] = None
    micro_lesson: Optional[str] = None
    history: List[Dict[str, Any]]
