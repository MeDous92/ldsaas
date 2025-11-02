from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Employee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: Optional[str] = None
# models.py


# ---- keep your existing models above (e.g., Employee) ----

class User(SQLModel, table=True):
    __tablename__ = "users"  # <- change if your real table name differs
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    username: str = Field(index=True)
    password_hash: str
    is_active: bool = True
    created_at: Optional[datetime] = None

class Invite(SQLModel, table=True):
    __tablename__ = "invites"  # <- change if needed
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    username: str
    token: str = Field(index=True)
    status: str = "pending"                # pending | accepted | expired | revoked
    expires_at: datetime
    created_at: Optional[datetime] = None