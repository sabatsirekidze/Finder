"""Phase A: core dating schema (users, profiles, swipes, matches, messages).

Revision ID: 001_phase_a
Revises:
Create Date: 2026-05-07

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_phase_a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "profiles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("gender", sa.String(length=40), nullable=True),
        sa.Column("looking_for", sa.String(length=40), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_table(
        "swipes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("swiper_user_id", sa.Integer(), nullable=False),
        sa.Column("target_user_id", sa.Integer(), nullable=False),
        sa.Column("direction", sa.String(length=10), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("swiper_user_id <> target_user_id", name="ck_swipe_not_self"),
        sa.CheckConstraint("direction IN ('like', 'pass')", name="ck_swipe_direction"),
        sa.ForeignKeyConstraint(["swiper_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("swiper_user_id", "target_user_id", name="uq_swipe_pair"),
    )
    op.create_index("ix_swipes_swiper_user_id", "swipes", ["swiper_user_id"])
    op.create_index("ix_swipes_target_user_id", "swipes", ["target_user_id"])
    op.create_index("ix_swipes_target_created", "swipes", ["target_user_id", "created_at"])

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_low_id", sa.Integer(), nullable=False),
        sa.Column("user_high_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("user_low_id < user_high_id", name="ck_match_order"),
        sa.ForeignKeyConstraint(["user_low_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_high_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_low_id", "user_high_id", name="uq_match_pair"),
    )
    op.create_index("ix_matches_user_low_id", "matches", ["user_low_id"])
    op.create_index("ix_matches_user_high_id", "matches", ["user_high_id"])

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("sender_user_id", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_match_id", "messages", ["match_id"])
    op.create_index("ix_messages_sender_user_id", "messages", ["sender_user_id"])
    op.create_index("ix_messages_match_created", "messages", ["match_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_messages_match_created", table_name="messages")
    op.drop_index("ix_messages_sender_user_id", table_name="messages")
    op.drop_index("ix_messages_match_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_matches_user_high_id", table_name="matches")
    op.drop_index("ix_matches_user_low_id", table_name="matches")
    op.drop_table("matches")
    op.drop_index("ix_swipes_target_created", table_name="swipes")
    op.drop_index("ix_swipes_target_user_id", table_name="swipes")
    op.drop_index("ix_swipes_swiper_user_id", table_name="swipes")
    op.drop_table("swipes")
    op.drop_table("profiles")
    op.drop_table("users")
