# app/models.py
from __future__ import annotations

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

# We map the existing Postgres enum `user_role`
# ENUM defined by migrations: ('admin','manager','employee')
pg_user_role = PGEnum(
    "admin", "manager", "employee",
    name="user_role",
    create_type=False,  # do NOT try to create from the ORM
)

pg_user_status = PGEnum(
    "pending", "active", "inactive",
    name="user_status",
    create_type=False,  # enum already exists in DB; don't recreate from ORM
)

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)  # DB has CITEXT + unique
    name: Optional[str] = None
    status: str = Field(
        sa_column=Column(
            pg_user_status,
            nullable=False,
            server_default=text("'pending'::user_status"),  # enum default, not plain text
        )
    )

    # password_hash is nullable in DB so invited users can exist without a password
    password_hash: Optional[str] = Field(default=None)

    # Map to the existing enum column; keep a default of 'employee'
    role: str = Field(
        default="employee",
        sa_column=Column(pg_user_role, nullable=False, server_default="employee"),
    )

    is_active: bool = Field(default=True)

    created_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})
    updated_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})

    # Invite flow fields
    invited_at: Optional[datetime] = None
    invited_by: Optional[int] = None
    invite_token_hash: Optional[str] = None
    invite_expires_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
