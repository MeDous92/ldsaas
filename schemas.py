# app/schemas.py
from typing import Optional
from pydantic import BaseModel, EmailStr, constr
from enum import Enum

MAX_PWD_BYTES = 72

class UserStatus(str, Enum):
    pending = "pending"
    active = "active"
    inactive = "inactive"

class InviteIn(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class InviteOut(BaseModel):
    email: EmailStr
    token: str  # raw token (only returned once to the inviter)
    name: Optional[str] = None
    invite_url: Optional[str] = None

class AcceptInviteIn(BaseModel):
    email: constr(strip_whitespace=True)
    token: str
    password: constr(min_length=8, max_length=72)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    role: str
    is_active: bool
    status: UserStatus
    class Config:
        from_attributes = True

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class LoginOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut