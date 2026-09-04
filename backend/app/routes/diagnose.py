from fastapi import APIRouter, HTTPException
from typing import Optional
from app.db.init_db import get_session, save_session
from app.graph.loader import graph_store
from app.engine.state_machine import DiagnosticStateMachine
from app.engine.traversal import traversal_engine
from app.engine.llm_calls import LLMDiagnosticService
from app.models.schemas import (
    ProbingAnswerRequest,
    GapClassificationResult,
    TeachBackRequest,
    TeachBackGradingResult,
    SessionStateResponse,
)
from app.models.db_models import SessionState
from app.routes.session import _build_session_response

router = APIRouter(prefix="/api/session", tags=["Diagnosis"])


@router.get("/{session_id}/diagnostic-step")
async def get_diagnostic_step(session_id: str):
    """Returns current active probing question and candidate node being evaluated."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    candidate = graph_store.get_node(session.current_candidate_node_id) if session.current_candidate_node_id else None
    return {
        "session_id": session.session_id,
        "state": session.state.value,
        "candidate_node": candidate,
        "probing_question": session.probing_question,
        "traversal_path": session.traversal_path,
        "diagnosed_gap_node_id": session.diagnosed_gap_node_id,
    }


@router.post("/{session_id}/answer-probing")
async def answer_probing_question(session_id: str, req: ProbingAnswerRequest):
    """
    Processes learner's answer to a probing question.
    - If gap detected: isolates gap and transitions to TEACHING.
    - If no gap: advances backward BFS traversal to the next prerequisite.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    if session.state != SessionState.DIAGNOSING:
        raise HTTPException(status_code=400, detail=f"Cannot answer probing question in state '{session.state.value}'")

    if not session.current_candidate_node_id or not session.probing_question:
        raise HTTPException(status_code=400, detail="No active probing question to answer")

    candidate = graph_store.get_node(session.current_candidate_node_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate node '{session.current_candidate_node_id}' not found")

    # Classify response using grounded tool call
    eval_res = await LLMDiagnosticService.classify_gap(
        node=candidate,
        question=session.probing_question,
        student_answer=req.answer,
    )

    if eval_res.gap_detected:
        # Gap found! Isolate gap and advance to TEACHING
        session.diagnosed_gap_node_id = candidate.id
        session = DiagnosticStateMachine.transition(
            session,
            SessionState.TEACHING,
            event_data={"gap_diagnosed": candidate.id, "reasoning": eval_res.reasoning}
        )
    else:
        # Candidate mastered! Advance BFS to next candidate
        if candidate.id not in session.mastered_nodes:
            session.mastered_nodes.append(candidate.id)

        next_candidate = traversal_engine.get_next_candidate(
            target_node_id=session.target_node_id,
            visited_in_session=session.traversal_path,
            mastered_nodes=session.mastered_nodes,
        )

        if next_candidate:
            probing_res = await LLMDiagnosticService.generate_probing_question(next_candidate)
            session.current_candidate_node_id = next_candidate.id
            session.probing_question = probing_res.question
            if next_candidate.id not in session.traversal_path:
                session.traversal_path.append(next_candidate.id)
            save_session(session)
        else:
            # Reached depth limit without finding gap; closest match fallback
            session.diagnosed_gap_node_id = candidate.id
            session = DiagnosticStateMachine.transition(
                session,
                SessionState.TEACHING,
                event_data={"gap_diagnosed_fallback": candidate.id}
            )

    return {
        "evaluation": eval_res,
        "session": _build_session_response(session),
    }


@router.get("/{session_id}/micro-lesson")
async def get_micro_lesson(session_id: str):
    """Retrieves micro-lesson copy and examples for the diagnosed gap node."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    if not session.diagnosed_gap_node_id:
        raise HTTPException(status_code=400, detail="No gap has been diagnosed yet")

    gap_node = graph_store.get_node(session.diagnosed_gap_node_id)
    if not gap_node:
        raise HTTPException(status_code=404, detail=f"Diagnosed gap node '{session.diagnosed_gap_node_id}' not found")

    return {
        "concept_id": gap_node.id,
        "name": gap_node.name,
        "micro_lesson": gap_node.micro_lesson,
        "teach_back_rubric": gap_node.teach_back_rubric,
    }


@router.post("/{session_id}/teach-back")
async def submit_teach_back(session_id: str, req: TeachBackRequest):
    """
    Submits student's teach-back explanation for rubric-grounded AI evaluation.
    - If understood: marks gap mastered and transitions to RE_TEST.
    - If not understood: requests retry with targeted feedback.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    if session.state not in (SessionState.TEACHING, SessionState.TEACH_BACK):
        raise HTTPException(status_code=400, detail=f"Cannot submit teach-back in state '{session.state.value}'")

    if session.state == SessionState.TEACHING:
        session = DiagnosticStateMachine.transition(session, SessionState.TEACH_BACK)

    gap_node = graph_store.get_node(session.diagnosed_gap_node_id)
    if not gap_node:
        raise HTTPException(status_code=404, detail="Diagnosed gap node not found")

    # Grade explanation using grounded tool call
    grading_res = await LLMDiagnosticService.grade_teach_back(
        node=gap_node,
        student_explanation=req.explanation,
    )

    if grading_res.understood:
        if gap_node.id not in session.mastered_nodes:
            session.mastered_nodes.append(gap_node.id)
        session = DiagnosticStateMachine.transition(
            session,
            SessionState.RE_TEST,
            event_data={"rubric_feedback": grading_res.feedback}
        )
    else:
        # Stay in TEACH_BACK for revision
        save_session(session)

    return {
        "grading": grading_res,
        "session": _build_session_response(session),
    }
