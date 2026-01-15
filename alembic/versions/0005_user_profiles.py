"""user profile and reference data

Revision ID: 0005_user_profiles
Revises: 0004_allow_assigned_status
Create Date: 2026-01-13 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_user_profiles"
down_revision: Union[str, None] = "0004_allow_assigned_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "education_levels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"]),
    )
    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("profile_picture_url", sa.String(), nullable=True),
        sa.Column("bio", sa.String(), nullable=True),
        sa.Column("education_level_id", sa.Integer(), nullable=True),
        sa.Column("address_line1", sa.String(), nullable=True),
        sa.Column("address_line2", sa.String(), nullable=True),
        sa.Column("postal_code", sa.String(), nullable=True),
        sa.Column("city_id", sa.Integer(), nullable=True),
        sa.Column("country_id", sa.Integer(), nullable=True),
        sa.Column("phone_number", sa.String(), nullable=True),
        sa.Column("personal_email", sa.String(), nullable=True),
        sa.Column("date_of_birth", sa.DateTime(), nullable=True),
        sa.Column("attribute1", sa.String(), nullable=True),
        sa.Column("attribute2", sa.String(), nullable=True),
        sa.Column("attribute3", sa.String(), nullable=True),
        sa.Column("attribute4", sa.String(), nullable=True),
        sa.Column("attribute5", sa.String(), nullable=True),
        sa.Column("attribute6", sa.String(), nullable=True),
        sa.Column("attribute7", sa.String(), nullable=True),
        sa.Column("attribute8", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["education_level_id"], ["education_levels.id"]),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"]),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"]),
    )
    op.create_table(
        "user_personal_emails",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_table(
        "user_dependents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("relationship", sa.String(), nullable=True),
        sa.Column("date_of_birth", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )

    # --- POPULATE REFERENCE DATA ---
    # We use a raw connection to insert data immediately
    # Education Levels
    op.bulk_insert(
        sa.table("education_levels", sa.column("name")),
        [
            {"name": "High School"},
            {"name": "Bachelor's Degree"},
            {"name": "Master's Degree"},
            {"name": "PhD"},
            {"name": "Vocational Training"},
        ]
    )

    # Countries
    # We need IDs for cities, but if we assume autoincrement starts at 1...
    # Better to insert and hope for sequential IDs or use raw SQL?
    # Bulk insert allows defining IDs if we want to be safe for foreign keys.
    op.bulk_insert(
        sa.table("countries", sa.column("id"), sa.column("name"), sa.column("code")),
        [
            {"id": 1, "name": "France", "code": "FR"},
            {"id": 2, "name": "United States", "code": "US"},
            {"id": 3, "name": "United Kingdom", "code": "UK"},
            {"id": 4, "name": "Germany", "code": "DE"},
            {"id": 5, "name": "Canada", "code": "CA"},
        ]
    )

    # Cities
    op.bulk_insert(
        sa.table("cities", sa.column("country_id"), sa.column("name")),
        [
            {"country_id": 1, "name": "Paris"},
            {"country_id": 1, "name": "Lyon"},
            {"country_id": 1, "name": "Marseille"},
            {"country_id": 2, "name": "New York"},
            {"country_id": 2, "name": "San Francisco"},
            {"country_id": 3, "name": "London"},
            {"country_id": 4, "name": "Berlin"},
            {"country_id": 5, "name": "Toronto"},
        ]
    )


def downgrade() -> None:
    op.drop_table("user_dependents")
    op.drop_table("user_personal_emails")
    op.drop_table("user_profiles")
    op.drop_table("cities")
    op.drop_table("countries")
    op.drop_table("education_levels")
