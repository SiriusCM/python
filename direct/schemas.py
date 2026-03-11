from pydantic import BaseModel
from typing import Optional

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    nickname: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class ProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

class PostCreate(BaseModel):
    content: str