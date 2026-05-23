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
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.enums import (
    HOBBY,
    PROFILE_GENDER,
    SWIPE_DIRECTION,
    Hobby,
    ProfileGender,
    SwipeDirection,
)

profile_gender_type = ENUM(
    ProfileGender, name=PROFILE_GENDER, create_type=False, values_callable=lambda x: [e.value for e in x]
)
hobby_type = ENUM(
    Hobby, name=HOBBY, create_type=False, values_callable=lambda x: [e.value for e in x]
)
swipe_direction_type = ENUM(
    SwipeDirection, name=SWIPE_DIRECTION, create_type=False, values_callable=lambda x: [e.value for e in x]
)


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
    hobbies: Mapped[list[ProfileHobby]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
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
    gender: Mapped[ProfileGender | None] = mapped_column(profile_gender_type)
    height_cm: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="profile")


class DatingPreferences(Base):
    """Stated partner filters (scalar row); multi-valued filters in child tables (1NF)."""

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
    prefer_same_city: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="dating_preferences")
    partner_genders: Mapped[list[DatingPreferenceGender]] = relationship(
        back_populates="preferences", cascade="all, delete-orphan"
    )
    partner_hobbies: Mapped[list[DatingPreferenceHobby]] = relationship(
        back_populates="preferences", cascade="all, delete-orphan"
    )


class DatingPreferenceGender(Base):
    __tablename__ = "dating_preference_genders"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("dating_preferences.user_id", ondelete="CASCADE"), primary_key=True
    )
    gender: Mapped[ProfileGender] = mapped_column(profile_gender_type, primary_key=True)

    preferences: Mapped[DatingPreferences] = relationship(back_populates="partner_genders")


class DatingPreferenceHobby(Base):
    __tablename__ = "dating_preference_hobbies"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("dating_preferences.user_id", ondelete="CASCADE"), primary_key=True
    )
    hobby: Mapped[Hobby] = mapped_column(hobby_type, primary_key=True)

    preferences: Mapped[DatingPreferences] = relationship(back_populates="partner_hobbies")


class ProfileHobby(Base):
    __tablename__ = "profile_hobbies"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    hobby: Mapped[Hobby] = mapped_column(hobby_type, primary_key=True)

    user: Mapped[User] = relationship(back_populates="hobbies")


class Swipe(Base):
    __tablename__ = "swipes"
    __table_args__ = (
        UniqueConstraint("swiper_user_id", "target_user_id", name="uq_swipe_pair"),
        CheckConstraint("swiper_user_id <> target_user_id", name="ck_swipe_not_self"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    swiper_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    direction: Mapped[SwipeDirection] = mapped_column(swipe_direction_type, nullable=False)
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
