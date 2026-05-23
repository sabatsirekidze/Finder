"""Fix missing dating_preference_genders table and orphaned indexes.

The DB was partially initialized — migration 002 created the dating_preferences
row but the child tables and their indexes were never applied. This migration
adds the missing table and drops orphaned indexes left from that inconsistency.

Revision ID: 005_fix_missing_tables
Revises: 004_hobbies
Create Date: 2026-05-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005_fix_missing_tables"
down_revision: Union[str, None] = "004_hobbies"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

profile_gender = postgresql.ENUM(
    "woman", "man", "nonbinary", name="profile_gender", create_type=False
)


def upgrade() -> None:
    # Drop orphaned indexes that ended up on the wrong table
    op.execute("DROP INDEX IF EXISTS ix_dating_preferences_partner_genders")
    op.execute("DROP INDEX IF EXISTS ix_dating_preferences_partner_hair_colors")

    # Create the missing child table
    op.execute("""
        CREATE TABLE IF NOT EXISTS dating_preference_genders (
            user_id INTEGER NOT NULL
                REFERENCES dating_preferences(user_id) ON DELETE CASCADE,
            gender profile_gender NOT NULL,
            PRIMARY KEY (user_id, gender)
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_dating_preference_genders_gender "
        "ON dating_preference_genders (gender)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_dating_preference_genders_gender")
    op.execute("DROP TABLE IF EXISTS dating_preference_genders")
