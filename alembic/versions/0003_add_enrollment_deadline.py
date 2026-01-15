"""add enrollment deadline

Revision ID: 0003_add_enrollment_deadline
Revises: 0002_expand_courses
Create Date: 2026-01-12 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_add_enrollment_deadline"
down_revision: Union[str, None] = "0002_expand_courses"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("course_enrollments", sa.Column("deadline", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("course_enrollments", "deadline")
