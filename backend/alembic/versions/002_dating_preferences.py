"""Partner preference row + profile traits for analytics (age, gender, hair, etc.).

Revision ID: 002_dating_preferences
Revises: 001_phase_a
Create Date: 2026-05-07

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002_dating_preferences"
down_revision: Union[str, None] = "001_phase_a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("profiles", sa.Column("hair_color", sa.String(length=40), nullable=True))
    op.add_column("profiles", sa.Column("height_cm", sa.Integer(), nullable=True))
    op.create_check_constraint(
        "ck_profiles_height_cm",
        "profiles",
        "height_cm IS NULL OR (height_cm BETWEEN 120 AND 230)",
    )
    op.create_index("ix_profiles_hair_color", "profiles", ["hair_color"])

    op.create_table(
        "dating_preferences",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("partner_age_min", sa.Integer(), nullable=True),
        sa.Column("partner_age_max", sa.Integer(), nullable=True),
        sa.Column("partner_genders", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("partner_hair_colors", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column(
            "prefer_same_city",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "partner_age_min IS NULL OR partner_age_min BETWEEN 18 AND 99",
            name="ck_dp_partner_age_min",
        ),
        sa.CheckConstraint(
            "partner_age_max IS NULL OR partner_age_max BETWEEN 18 AND 99",
            name="ck_dp_partner_age_max",
        ),
        sa.CheckConstraint(
            "partner_age_min IS NULL OR partner_age_max IS NULL OR partner_age_min <= partner_age_max",
            name="ck_dp_partner_age_order",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(
        "ix_dating_preferences_partner_genders",
        "dating_preferences",
        ["partner_genders"],
        unique=False,
        postgresql_using="gin",
    )
    op.create_index(
        "ix_dating_preferences_partner_hair_colors",
        "dating_preferences",
        ["partner_hair_colors"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_dating_preferences_partner_hair_colors", table_name="dating_preferences")
    op.drop_index("ix_dating_preferences_partner_genders", table_name="dating_preferences")
    op.drop_table("dating_preferences")
    op.drop_index("ix_profiles_hair_color", table_name="profiles")
    op.drop_constraint("ck_profiles_height_cm", "profiles", type_="check")
    op.drop_column("profiles", "height_cm")
    op.drop_column("profiles", "hair_color")
