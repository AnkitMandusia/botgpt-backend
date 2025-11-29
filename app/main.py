import os
import json
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import SessionLocal, Base, engine
from .models import User, Conversation, Message, Document
from .schemas import *
from .utils import estimate_tokens, chunk_text, retrieve_relevant_chunks
from .schemas import (
    UserCreate, UserOut, ConversationCreate, MessageCreate,
    ChatResponse, ConversationOut, MessageOut
)
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="BOT GPT - Conversational Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_groq(messages: list, max_tokens=1024):
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens
        )
        content = resp.choices[0].message.content
        tokens = resp.usage.total_tokens if resp.usage else estimate_tokens(content)
        return content, tokens
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LLM unavailable: {str(e)}")

def build_prompt(history: List[Message], retrieved: str = "") -> list:
    system = "You are a helpful assistant."
    if retrieved:
        system += "\n\nUse ONLY this context to answer:\n" + retrieved
    msgs = [{"role": m.role, "content": m.content} for m in history]
    return [{"role": "system", "content": system}] + msgs

@app.get("/")
async def root():
    return {"message": "BOT GPT Backend running! /docs"}

@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(400, "Username taken")
    db_user = User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/conversations", response_model=ChatResponse)
def create_conversation(req: ConversationCreate, db: Session = Depends(get_db)):
    user = db.get(User, req.user_id)
    if not user:
        raise HTTPException(404, "User not found")

    conv = Conversation(user_id=req.user_id, mode=req.mode, title=req.first_message[:50])
    db.add(conv)
    db.commit()
    db.refresh(conv)

    if req.mode == "grounded" and req.document_content:
        chunks = chunk_text(req.document_content)
        doc = Document(conversation_id=conv.id, original_text=req.document_content, chunks=json.dumps(chunks))
        db.add(doc)

    user_msg = Message(conversation_id=conv.id, role="user", content=req.first_message,
                       token_count=estimate_tokens(req.first_message))
    db.add(user_msg)
    db.commit()

    retrieved = ""
    if req.mode == "grounded" and req.document_content:
        retrieved = retrieve_relevant_chunks(req.first_message, chunks)

    reply, tokens = call_groq(build_prompt([user_msg], retrieved))
    assistant_msg = Message(conversation_id=conv.id, role="assistant", content=reply, token_count=tokens)
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(conversation_id=conv.id, response=reply)

# ... (other endpoints exactly same as before, just using Depends(get_db))

@app.get("/conversations", response_model=List[ConversationOut])
def list_conversations(user_id: int, db: Session = Depends(get_db), skip: int=0, limit: int=20):
    return db.query(Conversation).filter(Conversation.user_id == user_id).offset(skip).limit(limit).all()

@app.get("/conversations/{conv_id}")
def get_conversation(conv_id: int, db: Session = Depends(get_db)):
    msgs = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.created_at).all()
    if not msgs:
        raise HTTPException(404, "Not found")
    conv = msgs[0].conversation
    return {
        "conversation_id": conv_id,
        "mode": conv.mode,
        "messages": [{"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in msgs]
    }

@app.post("/conversations/{conv_id}/messages")
def send_message(conv_id: int, payload: MessageCreate, db: Session = Depends(get_db)):
    conv = db.get(Conversation, conv_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")

    user_msg = Message(conversation_id=conv_id, role="user", content=payload.message,
                       token_count=estimate_tokens(payload.message))
    db.add(user_msg)
    db.commit()

    history = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.created_at).all()
    recent = history[-12:]  # token-aware would be better, but safe

    retrieved = ""
    if conv.mode == "grounded" and conv.document and conv.document.chunks:
        chunks = json.loads(conv.document.chunks)
        retrieved = retrieve_relevant_chunks(payload.message, chunks)

    reply, tokens = call_groq(build_prompt(recent, retrieved))

    assistant_msg = Message(conversation_id=conv_id, role="assistant", content=reply, token_count=tokens)
    db.add(assistant_msg)
    db.commit()

    return {"response": reply}

@app.delete("/conversations/{conv_id}", status_code=204)
def delete_conversation(conv_id: int, db: Session = Depends(get_db)):
    conv = db.get(Conversation, conv_id)
    if not conv:
        raise HTTPException(404)
    db.delete(conv)
    db.commit()
    return None
