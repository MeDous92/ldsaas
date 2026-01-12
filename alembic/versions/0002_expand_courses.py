"""expand courses and providers

Revision ID: 0002_expand_courses
Revises: 0001_baseline
Create Date: 2026-01-12 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = "0002_expand_courses"
down_revision: Union[str, None] = "0001_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "course_providers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "course_classifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "course_flags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "course_duration_units",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    op.add_column("courses", sa.Column("description", sa.String(), nullable=True))
    op.add_column("courses", sa.Column("provider_id", sa.Integer(), nullable=True))
    op.add_column("courses", sa.Column("link", sa.String(), nullable=True))
    op.add_column("courses", sa.Column("image", sa.String(), nullable=True))
    op.add_column("courses", sa.Column("duration", sa.Integer(), nullable=True))
    op.add_column("courses", sa.Column("duration_unit_id", sa.Integer(), nullable=True))
    op.add_column("courses", sa.Column("skills", JSONB(), nullable=True))
    op.add_column("courses", sa.Column("competencies", JSONB(), nullable=True))
    op.add_column("courses", sa.Column("classification_id", sa.Integer(), nullable=True))
    op.add_column("courses", sa.Column("flag_id", sa.Integer(), nullable=True))
    op.add_column(
        "courses",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.add_column(
        "courses",
        sa.Column(
            "assigned_by_manager",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.add_column("courses", sa.Column("assigned_by_manager_id", sa.Integer(), nullable=True))
    op.add_column("courses", sa.Column("attribute1", sa.String(), nullable=True))
    op.add_column("courses", sa.Column("attribute2", sa.String(), nullable=True))
    op.add_column("courses", sa.Column("attribute3", sa.String(), nullable=True))
    op.add_column("courses", sa.Column("attribute4", sa.String(), nullable=True))
    op.add_column("courses", sa.Column("attribute5", sa.String(), nullable=True))
    op.add_column("courses", sa.Column("attribute6", sa.String(), nullable=True))
    op.add_column("courses", sa.Column("attribute7", sa.String(), nullable=True))
    op.add_column(
        "courses",
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_foreign_key(
        "courses_provider_id_fkey",
        "courses",
        "course_providers",
        ["provider_id"],
        ["id"],
    )
    op.create_foreign_key(
        "courses_duration_unit_id_fkey",
        "courses",
        "course_duration_units",
        ["duration_unit_id"],
        ["id"],
    )
    op.create_foreign_key(
        "courses_classification_id_fkey",
        "courses",
        "course_classifications",
        ["classification_id"],
        ["id"],
    )
    op.create_foreign_key(
        "courses_flag_id_fkey",
        "courses",
        "course_flags",
        ["flag_id"],
        ["id"],
    )
    op.create_foreign_key(
        "courses_assigned_by_manager_id_fkey",
        "courses",
        "users",
        ["assigned_by_manager_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("courses_assigned_by_manager_id_fkey", "courses", type_="foreignkey")
    op.drop_constraint("courses_flag_id_fkey", "courses", type_="foreignkey")
    op.drop_constraint("courses_classification_id_fkey", "courses", type_="foreignkey")
    op.drop_constraint("courses_duration_unit_id_fkey", "courses", type_="foreignkey")
    op.drop_constraint("courses_provider_id_fkey", "courses", type_="foreignkey")

    op.drop_column("courses", "updated_at")
    op.drop_column("courses", "attribute7")
    op.drop_column("courses", "attribute6")
    op.drop_column("courses", "attribute5")
    op.drop_column("courses", "attribute4")
    op.drop_column("courses", "attribute3")
    op.drop_column("courses", "attribute2")
    op.drop_column("courses", "attribute1")
    op.drop_column("courses", "assigned_by_manager_id")
    op.drop_column("courses", "assigned_by_manager")
    op.drop_column("courses", "is_active")
    op.drop_column("courses", "flag_id")
    op.drop_column("courses", "classification_id")
    op.drop_column("courses", "competencies")
    op.drop_column("courses", "skills")
    op.drop_column("courses", "duration_unit_id")
    op.drop_column("courses", "duration")
    op.drop_column("courses", "image")
    op.drop_column("courses", "link")
    op.drop_column("courses", "provider_id")
    op.drop_column("courses", "description")

    op.drop_table("course_duration_units")
    op.drop_table("course_flags")
    op.drop_table("course_classifications")
    op.drop_table("course_providers")
