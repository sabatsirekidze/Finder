"""Postgres ENUM labels — keep in sync with Alembic and db/schema.sql."""

from __future__ import annotations

import enum

# Postgres type names
PROFILE_GENDER = "profile_gender"
HOBBY = "hobby"
SWIPE_DIRECTION = "swipe_direction"


class ProfileGender(str, enum.Enum):
    WOMAN = "woman"
    MAN = "man"
    NONBINARY = "nonbinary"


class Hobby(str, enum.Enum):
    HIKING = "hiking"
    GAMING = "gaming"
    COOKING = "cooking"
    READING = "reading"
    TRAVEL = "travel"
    MUSIC = "music"
    SPORTS = "sports"
    ART = "art"
    FITNESS = "fitness"
    PHOTOGRAPHY = "photography"
    YOGA = "yoga"
    DANCING = "dancing"
    MOVIES = "movies"
    PETS = "pets"


class SwipeDirection(str, enum.Enum):
    SMASH = "smash"
    PASS = "pass"
