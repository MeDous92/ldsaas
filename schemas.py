from pydantic import BaseModel, EmailStr
from typing import Optional

class InviteIn(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class InviteOut(BaseModel):
    email: EmailStr
    token: str  # plain token returned to the inviter (e.g., to email out)

class AcceptInviteIn(BaseModel):
    email: EmailStr
    token: str
    password: str
    name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    role: str
    is_active: bool

class TokensOut(BaseModel):  # keep for later JWT integration
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    email: EmailStr
    password: str