from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, EmailStr

from app.enums import Hobby, ProfileGender, SwipeDirection


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class ProfileOut(BaseModel):
    user_id: int
    display_name: str
    bio: str | None
    birth_date: date | None
    city: str | None
    gender: ProfileGender | None
    height_cm: int | None
    hobbies: list[Hobby]
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    birth_date: date | None = None
    city: str | None = None
    gender: ProfileGender | None = None
    height_cm: int | None = None
    hobbies: list[Hobby] | None = None


# ---------------------------------------------------------------------------
# Dating preferences
# ---------------------------------------------------------------------------

class DatingPreferencesOut(BaseModel):
    partner_age_min: int | None
    partner_age_max: int | None
    prefer_same_city: bool
    partner_genders: list[ProfileGender]
    partner_hobbies: list[Hobby]

    model_config = {"from_attributes": True}


class DatingPreferencesUpdateRequest(BaseModel):
    partner_age_min: int | None = None
    partner_age_max: int | None = None
    prefer_same_city: bool | None = None
    partner_genders: list[ProfileGender] | None = None
    partner_hobbies: list[Hobby] | None = None


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

class DiscoveryBatch(BaseModel):
    profiles: list[ProfileOut]


# ---------------------------------------------------------------------------
# Swipes
# ---------------------------------------------------------------------------

class SwipeRequest(BaseModel):
    target_user_id: int
    direction: SwipeDirection


class SwipeResult(BaseModel):
    swipe_id: int
    match_created: bool
    match_id: int | None


# ---------------------------------------------------------------------------
# Matches
# ---------------------------------------------------------------------------

class MatchOut(BaseModel):
    id: int
    other_user_id: int
    other_display_name: str | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

class MessageRequest(BaseModel):
    body: str


class MessageOut(BaseModel):
    id: int
    match_id: int
    sender_user_id: int
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

class StatsOut(BaseModel):
    total_swipes_made: int
    smashes_received: int
    total_matches: int
    avg_messages_per_match: float | None
