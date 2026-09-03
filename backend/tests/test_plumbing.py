import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "mock_llm" in data
    assert "environment" in data


def test_plumbing_pass_payload():
    payload = {
        "code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n - 1)",
        "test_status": "PASS",
        "error_message": None,
        "execution_time_ms": 12.5,
    }
    response = client.post("/api/test-plumbing", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "acknowledged"
    assert data["observed_result"] == "PASS"
    assert "Plumbing handshake successful" in data["diagnostic_echo"]
    assert data["is_mock"] is True


def test_plumbing_fail_payload():
    payload = {
        "code": "def factorial(n):\n    return n * factorial(n - 1)",
        "test_status": "FAIL",
        "error_message": "RecursionError: maximum recursion depth exceeded",
        "execution_time_ms": 25.0,
    }
    response = client.post("/api/test-plumbing", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "acknowledged"
    assert data["observed_result"] == "FAIL"
    assert "RecursionError" in data["diagnostic_echo"]
    assert data["is_mock"] is True
