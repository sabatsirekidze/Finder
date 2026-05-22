"""Postgres ENUM labels — keep in sync with Alembic and db/schema.sql."""

from __future__ import annotations

import enum

# Postgres type names
PROFILE_GENDER = "profile_gender"
HAIR_COLOR = "hair_color"
LOOKING_FOR = "looking_for"
SWIPE_DIRECTION = "swipe_direction"


class ProfileGender(str, enum.Enum):
    WOMAN = "woman"
    MAN = "man"
    NONBINARY = "nonbinary"


class HairColor(str, enum.Enum):
    BLACK = "black"
    BROWN = "brown"
    BLONDE = "blonde"
    RED = "red"
    GRAY = "gray"
    OTHER = "other"


class LookingFor(str, enum.Enum):
    WOMEN = "women"
    MEN = "men"
    EVERYONE = "everyone"


class SwipeDirection(str, enum.Enum):
    SMASH = "smash"
    PASS = "pass"
