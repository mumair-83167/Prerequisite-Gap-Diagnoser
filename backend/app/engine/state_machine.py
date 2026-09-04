import time
import uuid
from typing import Optional, List, Dict, Any, Set
from app.models.db_models import SessionState, SessionRecord
from app.db.init_db import save_session, get_session


class InvalidStateTransitionError(ValueError):
    """Raised when an illegal state transition is attempted in the FSM."""
    pass


# Strict allowed transition mapping: current_state -> set(allowed_next_states)
ALLOWED_TRANSITIONS: Dict[SessionState, Set[SessionState]] = {
    SessionState.PRESENT_PROBLEM: {SessionState.AWAIT_RESULT},
    SessionState.AWAIT_RESULT: {SessionState.DIAGNOSING, SessionState.RESOLVED},
    SessionState.DIAGNOSING: {SessionState.DIAGNOSING, SessionState.TEACHING},
    SessionState.TEACHING: {SessionState.TEACH_BACK},
    SessionState.TEACH_BACK: {SessionState.TEACH_BACK, SessionState.RE_TEST},
    SessionState.RE_TEST: {SessionState.RESOLVED, SessionState.DIAGNOSING},
    SessionState.RESOLVED: set(),  # Terminal state
}


class DiagnosticStateMachine:
    """
    Controls and validates learner transitions across the 7 diagnostic states.
    All transitions persist automatically to the SQLite store.
    """

    @staticmethod
    def create_session(target_node_id: str = "recursion") -> SessionRecord:
        """Instantiates a fresh diagnostic session in PRESENT_PROBLEM state."""
        session = SessionRecord(
            session_id=str(uuid.uuid4()),
            state=SessionState.PRESENT_PROBLEM,
            target_node_id=target_node_id,
            diagnosed_gap_node_id=None,
            current_candidate_node_id=None,
            probing_question=None,
            traversal_path=[],
            mastered_nodes=[],
            history=[{"event": "session_created", "timestamp": time.time(), "target_node_id": target_node_id}],
        )
        return save_session(session)

    @staticmethod
    def transition(session: SessionRecord, to_state: SessionState, event_data: Optional[Dict[str, Any]] = None) -> SessionRecord:
        """Validates and executes a state transition."""
        allowed = ALLOWED_TRANSITIONS.get(session.state, set())
        if to_state not in allowed:
            raise InvalidStateTransitionError(
                f"Illegal transition from '{session.state.value}' to '{to_state.value}'. "
                f"Allowed destinations: {[s.value for s in allowed]}"
            )

        session.state = to_state
        session.updated_at = time.time()
        event_record = {
            "event": "transition",
            "from_state": session.state.value,
            "to_state": to_state.value,
            "timestamp": session.updated_at,
        }
        if event_data:
            event_record.update(event_data)
        session.history.append(event_record)

        return save_session(session)
