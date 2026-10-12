import pytest
from unittest.mock import patch, AsyncMock

def test_ai_status_endpoint(client):
    """Verify that /ai/status returns status structure."""
    response = client.get("/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert "model" in data


def test_reject_short_ai_question(client):
    """Verify rejection when question is too short."""
    response = client.post("/ai/ask", json={"question": "a"})
    assert response.status_code == 422


def test_reject_empty_ai_question(client):
    """Verify rejection when question is purely whitespace."""
    response = client.post("/ai/ask", json={"question": "   "})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ai_ask_fallback_when_ollama_offline(client):
    """
    Verify that when Ollama is offline, the endpoint still succeeds,
    returns deterministic database metrics, and marks service_available=False.
    """
    # Seed 2 students
    client.post("/students", json={"name": "Alice", "date_of_birth": "2000-01-01", "email": "alice@ai.edu", "course": "Robotics"})
    client.post("/students", json={"name": "Bob", "date_of_birth": "2000-01-01", "email": "bob@ai.edu", "course": "Robotics"})

    with patch("app.services.ollama_service.check_ollama_availability", new_callable=AsyncMock) as mock_avail:
        mock_avail.return_value = {"available": False, "version": None, "model": "llama3.2:1b"}

        response = client.post("/ai/ask", json={"question": "How many students are there?"})
        assert response.status_code == 200
        data = response.json()
        assert data["service_available"] is False
        assert data["is_grounded"] is True
        assert "2 student(s)" in data["answer"]
        assert data["exact_data_included"]["total_students"] == 2


@pytest.mark.asyncio
async def test_ai_ask_with_mocked_ollama_success(client):
    """
    Verify that when Ollama is reachable, the endpoint calls the model
    with grounded context and returns the model response.
    """
    client.post("/students", json={"name": "Charlie", "date_of_birth": "2002-05-12", "email": "charlie@ai.edu", "course": "Cybernetics"})

    with patch("app.services.ollama_service.check_ollama_availability", new_callable=AsyncMock) as mock_avail, \
         patch("app.services.ollama_service.query_ollama", new_callable=AsyncMock) as mock_query:

        mock_avail.return_value = {"available": True, "version": "0.1.28", "model": "llama3.2:1b"}
        mock_query.return_value = "Based on the records, there is 1 student enrolled in Cybernetics."

        response = client.post("/ai/ask", json={"question": "Summarize student records"})
        assert response.status_code == 200
        data = response.json()
        assert data["service_available"] is True
        assert data["is_grounded"] is True
        assert "1 student enrolled in Cybernetics" in data["answer"]
        assert data["model_used"] == "llama3.2:1b"
