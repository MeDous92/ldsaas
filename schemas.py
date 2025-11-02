# app/schemas.py
from typing import Optional
from pydantic import BaseModel, EmailStr

class InviteIn(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class InviteOut(BaseModel):
    email: EmailStr
    token: str  # raw token (only returned once to the inviter)

class AcceptInviteIn(BaseModel):
    email: EmailStr
    token: str
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    role: str
    is_active: bool
