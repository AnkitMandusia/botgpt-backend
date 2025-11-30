import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Optional: 
os.environ["ENV"] = "testing"

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_user():
    response = client.post("/users", json={"username": "testuser"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

    # Duplicate username
    resp2 = client.post("/users", json={"username": "testuser"})
    assert resp2.status_code == 400


def test_full_conversation_flow():
    # Create user
    user = client.post("/users", json={"username": "bob"}).json()
    user_id = user["id"]

    # Start conversation
    conv = client.post(
        "/conversations",
        json={"user_id": user_id, "first_message": "Hello BOT GPT", "mode": "open"}
    ).json()

    # REAL KEY RETURNED BY API:
    conv_id = conv["conversation_id"]
    assert conv_id > 0
    assert "response" in conv

    # Send follow-up message
    msg = client.post(
        f"/conversations/{conv_id}/messages",
        json={"message": "Tell me something cool"}
    )
    assert msg.status_code == 200
    assert "response" in msg.json()

    # List conversations
    convs = client.get(f"/conversations?user_id={user_id}").json()
    assert any(c["id"] == conv_id for c in convs)

    # Full history
    history = client.get(f"/conversations/{conv_id}").json()
    assert "messages" in history
    assert len(history["messages"]) >= 2

    # Delete conversation
    del_resp = client.delete(f"/conversations/{conv_id}")
    assert del_resp.status_code == 204
