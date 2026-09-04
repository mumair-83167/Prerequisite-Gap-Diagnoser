from fastapi import APIRouter, HTTPException, Query
from app.db.init_db import get_session, save_session
from app.graph.loader import graph_store
from app.engine.state_machine import DiagnosticStateMachine
from app.models.schemas import SessionStateResponse
from app.models.db_models import SessionState

router = APIRouter(prefix="/api/session", tags=["Session"])


def _build_session_response(session) -> SessionStateResponse:
    target_node = graph_store.get_node(session.target_node_id)
    gap_node = graph_store.get_node(session.diagnosed_gap_node_id) if session.diagnosed_gap_node_id else None

    return SessionStateResponse(
        session_id=session.session_id,
        state=session.state.value,
        target_node_id=session.target_node_id,
        diagnosed_gap_node_id=session.diagnosed_gap_node_id,
        current_candidate_node_id=session.current_candidate_node_id,
        probing_question=session.probing_question,
        traversal_path=session.traversal_path,
        mastered_nodes=session.mastered_nodes,
        problem=target_node.sample_problem if target_node else None,
        micro_lesson=gap_node.micro_lesson if gap_node else None,
        history=session.history,
    )


@router.post("/start", response_model=SessionStateResponse)
async def start_session(target_node_id: str = Query("recursion", description="Initial problem node ID")):
    """Initializes a new diagnostic session."""
    target_node = graph_store.get_node(target_node_id)
    if not target_node:
        raise HTTPException(status_code=404, detail=f"Target concept node '{target_node_id}' not found")

    session = DiagnosticStateMachine.create_session(target_node_id=target_node_id)
    return _build_session_response(session)


@router.get("/{session_id}", response_model=SessionStateResponse)
async def get_session_state(session_id: str):
    """Retrieves current session state and diagnostic progress."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    return _build_session_response(session)
