from unittest.mock import patch

@patch("app.main.groq_api_call")  # jo bhi function real call karta hai
def test_full_conversation_flow(mock_groq):
    mock_groq.return_value = {"reply": "Hello BOT GPT!"}
    
    user = client.post("/users", json={"username": "bob"}).json()
    user_id = user["id"]

    conv = client.post("/conversations", json={
        "user_id": user_id,
        "first_message": "Hello BOT GPT",
        "mode": "open"
    }).json()

    conv_id = conv.get("conversation_id")  # safer
    assert conv_id is not None
