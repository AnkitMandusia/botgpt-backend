from app.main import client

def test_full_conversation_flow():
    # create user
    user = client.post("/users", json={"username": "bob"}).json()
    user_id = user["id"]

    # create conversation
    conv = client.post("/conversations", json={
        "user_id": user_id,
        "first_message": "Hello BOT GPT",
        "mode": "open"
    }).json()

    assert "conversation_id" in conv
    assert conv["user_id"] == user_id
