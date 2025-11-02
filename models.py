from __future__ import annotations

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Enum as SAEnum, text

# Match Postgres enum name = user_role
class UserRole(str):
    admin = "admin"
    manager = "manager"
    employee = "employee"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)      # CITEXT in DB, fine to map as str
    name: Optional[str] = None
    password_hash: Optional[str] = None
    role: str = Field(
        default=UserRole.employee,
        sa_column_kwargs={"type_": SAEnum(UserRole.admin, UserRole.manager, UserRole.employee, name="user_role")}
    )
    is_active: bool = True

    created_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})
    updated_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})

    # invite-first flow fields
    invited_at: Optional[datetime] = None
    invited_by: Optional[int] = None
    invite_token_hash: Optional[str] = None
    invite_expires_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
