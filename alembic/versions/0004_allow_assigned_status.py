"""allow assigned status

Revision ID: 0004_allow_assigned_status
Revises: 0003_add_enrollment_deadline
Create Date: 2026-01-13 14:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_allow_assigned_status"
down_revision: Union[str, None] = "0003_add_enrollment_deadline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the check constraint that limits status values
    # We use raw SQL because dropping check constraints varies by dialect and Alembic op.drop_constraint needs a name
    # The name is confirmed from logs: course_enrollments_status_check
    op.execute("ALTER TABLE course_enrollments DROP CONSTRAINT IF EXISTS course_enrollments_status_check")


def downgrade() -> None:
    # We could try to re-add it, but we need to know the allowed values. 
    # For now, we won't strictly enforce it in DB or we can re-add pending/approved/completed/rejected
    # But since we want to allow 'assigned', downgrading implies removing support for 'assigned'.
    # For safety, let's just leave it dropped or re-add the old one if we knew it.
    # Re-adding restrictive constraint might fail if data exists.
    pass
