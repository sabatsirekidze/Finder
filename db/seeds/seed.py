"""
Load synthetic data (Faker). Run after migrations.

  cd backend
  ..\.venv\Scripts\python  ..\\db\\seeds\\seed.py    # Windows venv example
  python ../db/seeds/seed.py                         # from backend/, unix/venv

Requires DATABASE_URL in environment (.env next to docker-compose or export).
"""

from __future__ import annotations

import os
import random
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
load_dotenv(ROOT / ".env")

from app.enums import HairColor, LookingFor, ProfileGender, SwipeDirection  # noqa: E402
from app.models import (  # noqa: E402
    DatingPreferenceGender,
    DatingPreferenceHairColor,
    DatingPreferences,
    Match,
    Message,
    Profile,
    Swipe,
    User,
)

HAIR_COLORS = tuple(HairColor)
GENDERS = tuple(ProfileGender)
LOOKING_FOR_OPTIONS = tuple(LookingFor)


def age_years(birth: date, today: date | None = None) -> int:
    today = today or date.today()
    y = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        y -= 1
    return y


def main() -> None:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL missing — copy .env.example to .env")

    engine = create_engine(url, future=True)
    SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, future=True)

    fake = Faker()
    Faker.seed(42)
    random.seed(42)

    with SessionLocal() as session:
        if session.query(User).first():
            raise SystemExit("Database already has users — truncate tables or use a fresh DB.")

        n_users = 28
        users: list[User] = []
        for _ in range(n_users):
            u = User(email=fake.unique.email(), password_hash="seed-not-for-production")
            session.add(u)
            users.append(u)
        session.flush()

        profiles: list[Profile] = []
        for u in users:
            bd = fake.date_of_birth(minimum_age=18, maximum_age=45)
            profile = Profile(
                user_id=u.id,
                display_name=fake.first_name(),
                bio=fake.paragraph(nb_sentences=2),
                birth_date=bd,
                city=fake.city(),
                gender=random.choice([*GENDERS, None]),
                looking_for=random.choice([*LOOKING_FOR_OPTIONS, None]),
                hair_color=random.choice(HAIR_COLORS),
                height_cm=random.randint(155, 198),
            )
            session.add(profile)
            profiles.append(profile)
        session.flush()

        for p in profiles:
            if p.birth_date is None:
                continue
            my_age = age_years(p.birth_date)
            spread = random.randint(3, 8)
            p_min = max(18, my_age - spread)
            p_max = min(80, my_age + spread + random.randint(0, 5))
            if p_min > p_max:
                p_min, p_max = p_max, p_min
            g_choices = random.sample(GENDERS, k=random.randint(1, len(GENDERS)))
            h_choices = random.sample(HAIR_COLORS, k=random.randint(1, 4))
            session.add(
                DatingPreferences(
                    user_id=p.user_id,
                    partner_age_min=p_min,
                    partner_age_max=p_max,
                    prefer_same_city=random.random() < 0.35,
                )
            )
            for g in g_choices:
                session.add(DatingPreferenceGender(user_id=p.user_id, gender=g))
            for h in h_choices:
                session.add(DatingPreferenceHairColor(user_id=p.user_id, hair_color=h))

        ids = [u.id for u in users]
        seen_pairs: set[tuple[int, int]] = set()
        swipes: list[Swipe] = []
        target_swipes = min(420, len(ids) * (len(ids) - 1))
        while len(swipes) < target_swipes:
            a, b = random.sample(ids, 2)
            key = (a, b)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            direction = SwipeDirection.SMASH if random.random() < 0.52 else SwipeDirection.PASS
            swipes.append(Swipe(swiper_user_id=a, target_user_id=b, direction=direction))
        session.add_all(swipes)
        session.flush()

        smash_pairs = {
            (s.swiper_user_id, s.target_user_id)
            for s in swipes
            if s.direction == SwipeDirection.SMASH
        }
        mutual: set[tuple[int, int]] = set()
        for a, b in smash_pairs:
            if (b, a) in smash_pairs:
                mutual.add((a, b) if a < b else (b, a))

        matches: list[Match] = []
        for low, high in mutual:
            matches.append(Match(user_low_id=low, user_high_id=high))
        session.add_all(matches)
        session.flush()

        for m in matches:
            n_msg = random.randint(1, 10)
            sender_toggle = random.choice([m.user_low_id, m.user_high_id])
            for _ in range(n_msg):
                body = fake.sentence(nb_words=8)
                session.add(
                    Message(match_id=m.id, sender_user_id=sender_toggle, body=body)
                )
                sender_toggle = (
                    m.user_high_id if sender_toggle == m.user_low_id else m.user_low_id
                )

        session.commit()
        print(
            f"Seeded {len(users)} users + dating_preferences, {len(swipes)} swipes, "
            f"{len(matches)} matches, messages committed."
        )


if __name__ == "__main__":
    main()
