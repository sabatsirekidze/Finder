from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    profile: Mapped[Profile | None] = relationship(back_populates="user", uselist=False)
    dating_preferences: Mapped[DatingPreferences | None] = relationship(
        back_populates="user", uselist=False
    )
    swipes_made: Mapped[list[Swipe]] = relationship(
        foreign_keys="Swipe.swiper_user_id", back_populates="swiper"
    )


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        CheckConstraint(
            "height_cm IS NULL OR (height_cm BETWEEN 120 AND 230)",
            name="ck_profiles_height_cm",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text)
    birth_date: Mapped[date | None] = mapped_column(Date)
    city: Mapped[str | None] = mapped_column(String(120))
    gender: Mapped[str | None] = mapped_column(String(40))
    looking_for: Mapped[str | None] = mapped_column(String(40))
    hair_color: Mapped[str | None] = mapped_column(String(40))
    height_cm: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="profile")


class DatingPreferences(Base):
    """Stated partner filters; compare to actual partners via matches + their profiles."""

    __tablename__ = "dating_preferences"
    __table_args__ = (
        CheckConstraint(
            "partner_age_min IS NULL OR partner_age_min BETWEEN 18 AND 99",
            name="ck_dp_partner_age_min",
        ),
        CheckConstraint(
            "partner_age_max IS NULL OR partner_age_max BETWEEN 18 AND 99",
            name="ck_dp_partner_age_max",
        ),
        CheckConstraint(
            "partner_age_min IS NULL OR partner_age_max IS NULL OR partner_age_min <= partner_age_max",
            name="ck_dp_partner_age_order",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    partner_age_min: Mapped[int | None] = mapped_column(Integer)
    partner_age_max: Mapped[int | None] = mapped_column(Integer)
    partner_genders: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    partner_hair_colors: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    prefer_same_city: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="dating_preferences")


class Swipe(Base):
    __tablename__ = "swipes"
    __table_args__ = (
        UniqueConstraint("swiper_user_id", "target_user_id", name="uq_swipe_pair"),
        CheckConstraint("swiper_user_id <> target_user_id", name="ck_swipe_not_self"),
        CheckConstraint("direction IN ('like', 'pass')", name="ck_swipe_direction"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    swiper_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    swiper: Mapped[User] = relationship(foreign_keys=[swiper_user_id], back_populates="swipes_made")


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("user_low_id", "user_high_id", name="uq_match_pair"),
        CheckConstraint("user_low_id < user_high_id", name="ck_match_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_low_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user_high_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    messages: Mapped[list[Message]] = relationship(back_populates="match")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    match: Mapped[Match] = relationship(back_populates="messages")
