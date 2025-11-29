from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])

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

    model_config = {
        "populate_by_name": True,           
        "alias_generator": to_camel         
    }
