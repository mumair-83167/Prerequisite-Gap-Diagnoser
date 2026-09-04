import pytest
from app.db.init_db import init_db, get_session
from app.models.db_models import SessionState, SessionRecord
from app.engine.state_machine import DiagnosticStateMachine, InvalidStateTransitionError


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_session_lifecycle_happy_path():
    """Verify standard happy path transitions."""
    session = DiagnosticStateMachine.create_session("recursion")
    assert session.state == SessionState.PRESENT_PROBLEM
    assert session.target_node_id == "recursion"

    # PRESENT_PROBLEM -> AWAIT_RESULT
    session = DiagnosticStateMachine.transition(session, SessionState.AWAIT_RESULT)
    assert session.state == SessionState.AWAIT_RESULT

    # AWAIT_RESULT -> DIAGNOSING (student fails initial problem)
    session = DiagnosticStateMachine.transition(session, SessionState.DIAGNOSING)
    assert session.state == SessionState.DIAGNOSING

    # DIAGNOSING -> TEACHING (gap diagnosed)
    session.diagnosed_gap_node_id = "conditionals"
    session = DiagnosticStateMachine.transition(session, SessionState.TEACHING)
    assert session.state == SessionState.TEACHING

    # TEACHING -> TEACH_BACK
    session = DiagnosticStateMachine.transition(session, SessionState.TEACH_BACK)
    assert session.state == SessionState.TEACH_BACK

    # TEACH_BACK -> RE_TEST (passed teach-back)
    session.mastered_nodes.append("conditionals")
    session = DiagnosticStateMachine.transition(session, SessionState.RE_TEST)
    assert session.state == SessionState.RE_TEST

    # RE_TEST -> RESOLVED (passed re-test)
    session = DiagnosticStateMachine.transition(session, SessionState.RESOLVED)
    assert session.state == SessionState.RESOLVED

    # Check persistence in SQLite
    reloaded = get_session(session.session_id)
    assert reloaded is not None
    assert reloaded.state == SessionState.RESOLVED
    assert reloaded.diagnosed_gap_node_id == "conditionals"
    assert "conditionals" in reloaded.mastered_nodes


def test_illegal_transition_rejection():
    """Verify illegal transitions are strictly rejected by the FSM."""
    session = DiagnosticStateMachine.create_session("recursion")
    # Cannot jump directly from PRESENT_PROBLEM to RESOLVED or TEACHING
    with pytest.raises(InvalidStateTransitionError, match="Illegal transition"):
        DiagnosticStateMachine.transition(session, SessionState.RESOLVED)

    with pytest.raises(InvalidStateTransitionError, match="Illegal transition"):
        DiagnosticStateMachine.transition(session, SessionState.TEACHING)


def test_direct_pass_without_diagnosis():
    """Verify learner passing on first try transitions directly AWAIT_RESULT -> RESOLVED."""
    session = DiagnosticStateMachine.create_session("recursion")
    session = DiagnosticStateMachine.transition(session, SessionState.AWAIT_RESULT)
    session = DiagnosticStateMachine.transition(session, SessionState.RESOLVED)
    assert session.state == SessionState.RESOLVED
