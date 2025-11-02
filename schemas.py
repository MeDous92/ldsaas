from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr

Role = Literal["admin", "manager", "employee"]

class InviteIn(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    role: Optional[Role] = "employee"

class AcceptInviteIn(BaseModel):
    email: EmailStr
    token: str
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    role: str
    created_at: datetime

class TokensOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
