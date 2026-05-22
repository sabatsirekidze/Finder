"""Indexes for discovery / recommendation batch queries (Feature 1).

Revision ID: 003_discovery_indexes
Revises: 002_dating_preferences
Create Date: 2026-05-22

"""

from typing import Sequence, Union

from alembic import op

revision: str = "003_discovery_indexes"
down_revision: Union[str, None] = "002_dating_preferences"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_profiles_updated_at", "profiles", ["updated_at"])
    op.create_index("ix_profiles_city", "profiles", ["city"])


def downgrade() -> None:
    op.drop_index("ix_profiles_city", table_name="profiles")
    op.drop_index("ix_profiles_updated_at", table_name="profiles")
