from fastapi import APIRouter, HTTPException
from app.db.init_db import get_session, save_session
from app.graph.loader import graph_store
from app.engine.state_machine import DiagnosticStateMachine
from app.engine.traversal import traversal_engine
from app.engine.llm_calls import LLMDiagnosticService
from app.models.schemas import PlumbingTestRequest, SessionStateResponse
from app.models.db_models import SessionState
from app.routes.session import _build_session_response

router = APIRouter(prefix="/api/session", tags=["Submission"])


@router.post("/{session_id}/submit-code", response_model=SessionStateResponse)
async def submit_code(session_id: str, req: PlumbingTestRequest):
    """
    Receives Pyodide execution results.
    - If PASS: transitions to RESOLVED if on initial attempt or re-test.
    - If FAIL: transitions to DIAGNOSING, queries bounded BFS, and initiates first probing question.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    # If in PRESENT_PROBLEM, step into AWAIT_RESULT
    if session.state == SessionState.PRESENT_PROBLEM:
        session = DiagnosticStateMachine.transition(session, SessionState.AWAIT_RESULT)

    # Learner PASSED
    if req.test_status == "PASS":
        if session.state in (SessionState.AWAIT_RESULT, SessionState.RE_TEST):
            if session.target_node_id not in session.mastered_nodes:
                session.mastered_nodes.append(session.target_node_id)
            session = DiagnosticStateMachine.transition(
                session,
                SessionState.RESOLVED,
                event_data={"result": "PASS", "execution_time_ms": req.execution_time_ms}
            )
        return _build_session_response(session)

    # Learner FAILED
    if session.state in (SessionState.AWAIT_RESULT, SessionState.RE_TEST):
        session = DiagnosticStateMachine.transition(
            session,
            SessionState.DIAGNOSING,
            event_data={"result": "FAIL", "error": req.error_message}
        )

        # Get first candidate node from bounded BFS
        candidate = traversal_engine.get_next_candidate(
            target_node_id=session.target_node_id,
            visited_in_session=session.traversal_path,
            mastered_nodes=session.mastered_nodes,
        )

        if candidate:
            probing_res = await LLMDiagnosticService.generate_probing_question(candidate)
            session.current_candidate_node_id = candidate.id
            session.probing_question = probing_res.question
            if candidate.id not in session.traversal_path:
                session.traversal_path.append(candidate.id)
            save_session(session)
        else:
            # Fallback if no prerequisites
            session.diagnosed_gap_node_id = session.target_node_id
            session = DiagnosticStateMachine.transition(session, SessionState.TEACHING)

    return _build_session_response(session)
