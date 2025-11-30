from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@patch("app.main.groq_api_call")
def test_full_conversation_flow(mock_groq):
    mock_groq.return_value = {"reply": "Hello BOT GPT!"}

    user = client.post("/users", json={"username": "bob"}).json()
    user_id = user["id"]

    conv = client.post("/conversations", json={
        "user_id": user_id,
        "first_message": "Hello BOT GPT",
        "mode": "open"
    }).json()

    assert "conversation_id" in conv
