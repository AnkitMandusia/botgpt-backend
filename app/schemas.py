from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    username: str

class UserOut(BaseModel):
    id: int
    username: str

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

    class Config:
        populate_by_name = True  
        alias_generator = lambda field_name: "".join(
            word.capitalize() if i > 0 else word for i, word in enumerate(field_name.split("_"))
        )
