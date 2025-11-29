from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    username: str

class UserOut(BaseModel):
    id: int
    username: str

class MessageCreate(BaseModel):
    message: str

class ConversationCreate(BaseModel):
    user_id: int
    first_message: str
    mode: str = "open"
    document_content: Optional[str] = None

class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

class ConversationOut(BaseModel):
    id: int
    title: str
    mode: str
    created_at: datetime

class ChatResponse(BaseModel):
    conversation_id: int
    response: str