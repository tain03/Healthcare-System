from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatBase(BaseModel):
    user_id: int
    message: str

class ChatCreate(ChatBase):
    pass

class ChatResponse(BaseModel):
    response: str

class ChatMessage(ChatBase):
    id: int
    is_user: bool
    created_at: datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str
    full_name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True 