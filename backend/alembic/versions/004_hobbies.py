"""Replace hair_color + looking_for with hobbies.

Drops profiles.looking_for, profiles.hair_color, dating_preference_hair_colors,
hair_color enum, looking_for enum. Adds hobby enum, profile_hobbies table,
dating_preference_hobbies table.

Revision ID: 004_hobbies
Revises: 003_discovery_indexes
Create Date: 2026-05-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004_hobbies"
down_revision: Union[str, None] = "003_discovery_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_HOBBY_VALUES = (
    "hiking", "gaming", "cooking", "reading", "travel",
    "music", "sports", "art", "fitness", "photography",
    "yoga", "dancing", "movies", "pets",
)

hobby = postgresql.ENUM(*_HOBBY_VALUES, name="hobby", create_type=False)


def upgrade() -> None:
    # --- remove looking_for -----------------------------------------------
    op.execute("ALTER TABLE profiles DROP COLUMN IF EXISTS looking_for")
    postgresql.ENUM(name="looking_for").drop(op.get_bind(), checkfirst=True)

    # --- remove hair_color -------------------------------------------------
    op.execute("DROP INDEX IF EXISTS ix_profiles_hair_color")
    op.execute("ALTER TABLE profiles DROP COLUMN IF EXISTS hair_color")

    op.execute("DROP INDEX IF EXISTS ix_dating_preference_hair_colors_hair_color")
    op.execute("DROP TABLE IF EXISTS dating_preference_hair_colors")
    postgresql.ENUM(name="hair_color").drop(op.get_bind(), checkfirst=True)

    # --- add hobby enum and new tables ------------------------------------
    postgresql.ENUM(*_HOBBY_VALUES, name="hobby").create(op.get_bind(), checkfirst=True)

    op.create_table(
        "profile_hobbies",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("hobby", hobby, nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "hobby"),
    )
    op.create_index("ix_profile_hobbies_hobby", "profile_hobbies", ["hobby"])

    op.create_table(
        "dating_preference_hobbies",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("hobby", hobby, nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["dating_preferences.user_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "hobby"),
    )
    op.create_index(
        "ix_dating_preference_hobbies_hobby", "dating_preference_hobbies", ["hobby"]
    )


def downgrade() -> None:
    op.drop_index("ix_dating_preference_hobbies_hobby", table_name="dating_preference_hobbies")
    op.drop_table("dating_preference_hobbies")
    op.drop_index("ix_profile_hobbies_hobby", table_name="profile_hobbies")
    op.drop_table("profile_hobbies")
    postgresql.ENUM(name="hobby").drop(op.get_bind(), checkfirst=True)

    hair_color = postgresql.ENUM(
        "black", "brown", "blonde", "red", "gray", "other", name="hair_color"
    )
    hair_color.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "dating_preference_hair_colors",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("hair_color", hair_color, nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["dating_preferences.user_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "hair_color"),
    )
    op.create_index(
        "ix_dating_preference_hair_colors_hair_color",
        "dating_preference_hair_colors",
        ["hair_color"],
    )

    op.add_column("profiles", sa.Column("hair_color", hair_color, nullable=True))
    op.create_index("ix_profiles_hair_color", "profiles", ["hair_color"])

    postgresql.ENUM("women", "men", "everyone", name="looking_for").create(
        op.get_bind(), checkfirst=True
    )
    looking_for = postgresql.ENUM("women", "men", "everyone", name="looking_for", create_type=False)
    op.add_column("profiles", sa.Column("looking_for", looking_for, nullable=True))
