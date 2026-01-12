# app/models.py
from __future__ import annotations

from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import JSONB
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

class CourseProvider(SQLModel, table=True):
    __tablename__ = "course_providers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})
    updated_at: datetime = Field(
        sa_column_kwargs={"server_default": text("now()"), "onupdate": text("now()")}
    )


class CourseClassification(SQLModel, table=True):
    __tablename__ = "course_classifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})


class CourseFlag(SQLModel, table=True):
    __tablename__ = "course_flags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})


class CourseDurationUnit(SQLModel, table=True):
    __tablename__ = "course_duration_units"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})


class Course(SQLModel, table=True):
    __tablename__ = "courses"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    provider: Optional[str] = None  # legacy text provider name
    provider_id: Optional[int] = Field(default=None, foreign_key="course_providers.id")
    link: Optional[str] = None
    image: Optional[str] = None
    duration: Optional[int] = None
    duration_unit_id: Optional[int] = Field(default=None, foreign_key="course_duration_units.id")
    skills: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    competencies: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    classification_id: Optional[int] = Field(default=None, foreign_key="course_classifications.id")
    flag_id: Optional[int] = Field(default=None, foreign_key="course_flags.id")
    is_active: bool = Field(default=True)
    assigned_by_manager: bool = Field(default=False)
    assigned_by_manager_id: Optional[int] = Field(default=None, foreign_key="users.id")
    attribute1: Optional[str] = None
    attribute2: Optional[str] = None
    attribute3: Optional[str] = None
    attribute4: Optional[str] = None
    attribute5: Optional[str] = None
    attribute6: Optional[str] = None
    attribute7: Optional[str] = None
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})
    updated_at: datetime = Field(
        sa_column_kwargs={"server_default": text("now()"), "onupdate": text("now()")}
    )

class EmployeeManager(SQLModel, table=True):
    __tablename__ = "employee_managers"

    employee_id: int = Field(primary_key=True, foreign_key="users.id")
    manager_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})

class CourseEnrollment(SQLModel, table=True):
    __tablename__ = "course_enrollments"

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="users.id")
    course_id: int = Field(foreign_key="courses.id")
    status: str = Field(default="pending")
    requested_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = Field(default=None, foreign_key="users.id")

class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str
    body: str
    type: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(sa_column_kwargs={"server_default": text("now()")})
    meta: Optional[dict] = Field(default=None, sa_column=Column("metadata", JSONB))
