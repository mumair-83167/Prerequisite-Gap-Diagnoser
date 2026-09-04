import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_full_recursion_diagnostic_journey():
    """
    Verifies the complete end-to-end diagnostic lifecycle on the recursion demo path:
    1. Start session -> PRESENT_PROBLEM
    2. Student fails recursive factorial -> DIAGNOSING + Probing Question generated
    3. Student answers probing question with gap -> Diagnosed & transitions to TEACHING
    4. Fetch micro-lesson for diagnosed gap
    5. Student provides successful teach-back -> Evaluated & transitions to RE_TEST
    6. Student retries original problem and passes -> RESOLVED
    """
    # 1. Start Session
    start_resp = client.post("/api/session/start?target_node_id=recursion")
    assert start_resp.status_code == 200
    session_data = start_resp.json()
    session_id = session_data["session_id"]
    assert session_data["state"] == "PRESENT_PROBLEM"
    assert session_data["target_node_id"] == "recursion"
    assert session_data["problem"]["id"] == "factorial_recursive"

    # 2. Student Submits Buggy Code (Fails)
    fail_payload = {
        "code": "def factorial(n):\n    return n * factorial(n - 1)",
        "test_status": "FAIL",
        "error_message": "RecursionError: maximum recursion depth exceeded",
        "execution_time_ms": 32.4,
    }
    submit_resp = client.post(f"/api/session/{session_id}/submit-code", json=fail_payload)
    assert submit_resp.status_code == 200
    state_after_fail = submit_resp.json()
    assert state_after_fail["state"] == "DIAGNOSING"
    assert state_after_fail["current_candidate_node_id"] is not None
    assert state_after_fail["probing_question"] is not None
    assert len(state_after_fail["traversal_path"]) >= 1

    candidate_id = state_after_fail["current_candidate_node_id"]

    # 3. Check Diagnostic Step endpoint
    step_resp = client.get(f"/api/session/{session_id}/diagnostic-step")
    assert step_resp.status_code == 200
    step_data = step_resp.json()
    assert step_data["candidate_node"]["id"] == candidate_id

    # 4. Student Answers Probing Question (Shows Gap)
    answer_payload = {
        "answer": "I don't know why it fails, it just keeps repeating forever and throws an error."
    }
    answer_resp = client.post(f"/api/session/{session_id}/answer-probing", json=answer_payload)
    assert answer_resp.status_code == 200
    answer_data = answer_resp.json()
    assert answer_data["evaluation"]["gap_detected"] is True
    assert answer_data["session"]["state"] == "TEACHING"
    assert answer_data["session"]["diagnosed_gap_node_id"] == candidate_id

    # 5. Fetch Micro-Lesson
    lesson_resp = client.get(f"/api/session/{session_id}/micro-lesson")
    assert lesson_resp.status_code == 200
    lesson_data = lesson_resp.json()
    assert lesson_data["concept_id"] == candidate_id
    assert len(lesson_data["micro_lesson"]) > 20
    assert len(lesson_data["teach_back_rubric"]) >= 2

    # 6. Student Submits Teach-Back Explanation
    teach_back_payload = {
        "explanation": (
            "The base case is the essential condition that returns a fixed value without calling "
            "the function again, which prevents the function from calling itself forever."
        )
    }
    tb_resp = client.post(f"/api/session/{session_id}/teach-back", json=teach_back_payload)
    assert tb_resp.status_code == 200
    tb_data = tb_resp.json()
    assert tb_data["grading"]["understood"] is True
    assert tb_data["session"]["state"] == "RE_TEST"
    assert candidate_id in tb_data["session"]["mastered_nodes"]

    # 7. Student Retries and Passes
    pass_payload = {
        "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
        "test_status": "PASS",
        "error_message": None,
        "execution_time_ms": 14.1,
    }
    retest_resp = client.post(f"/api/session/{session_id}/submit-code", json=pass_payload)
    assert retest_resp.status_code == 200
    final_data = retest_resp.json()
    assert final_data["state"] == "RESOLVED"
    assert "recursion" in final_data["mastered_nodes"]
