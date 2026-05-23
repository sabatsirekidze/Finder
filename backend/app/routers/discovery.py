from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.enums import Hobby
from app.models import User
from app.schemas import DiscoveryBatch, ProfileOut

router = APIRouter()

_BATCH_SQL = text("""
    SELECT p.user_id, p.display_name, p.bio, p.birth_date, p.city,
           p.gender, p.height_cm, p.updated_at
    FROM profiles p
    LEFT JOIN dating_preferences dp ON dp.user_id = :me
    WHERE p.user_id <> :me
      AND NOT EXISTS (
          SELECT 1 FROM swipes s
          WHERE s.swiper_user_id = :me AND s.target_user_id = p.user_id
      )
      AND (
          dp.user_id IS NULL
          OR NOT dp.prefer_same_city
          OR p.city IS NOT DISTINCT FROM (SELECT city FROM profiles WHERE user_id = :me)
      )
      AND (
          dp.user_id IS NULL
          OR p.birth_date IS NULL
          OR dp.partner_age_min IS NULL OR dp.partner_age_max IS NULL
          OR EXTRACT(YEAR FROM age(p.birth_date))
             BETWEEN dp.partner_age_min AND dp.partner_age_max
      )
      AND (
          dp.user_id IS NULL
          OR NOT EXISTS (SELECT 1 FROM dating_preference_genders WHERE user_id = :me)
          OR p.gender IN (SELECT gender FROM dating_preference_genders WHERE user_id = :me)
      )
      AND (
          dp.user_id IS NULL
          OR NOT EXISTS (SELECT 1 FROM dating_preference_hobbies WHERE user_id = :me)
          OR EXISTS (
              SELECT 1 FROM profile_hobbies ph
              JOIN dating_preference_hobbies dph ON dph.hobby = ph.hobby
              WHERE ph.user_id = p.user_id AND dph.user_id = :me
          )
      )
    ORDER BY p.updated_at DESC NULLS LAST
    LIMIT 20
""")


@router.get("/batch", response_model=DiscoveryBatch)
def get_discovery_batch(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(_BATCH_SQL, {"me": current_user.id}).mappings().all()

    if not rows:
        return DiscoveryBatch(profiles=[])

    user_ids = [r["user_id"] for r in rows]
    hobbies_rows = db.execute(
        text("SELECT user_id, hobby FROM profile_hobbies WHERE user_id = ANY(:ids)"),
        {"ids": user_ids},
    ).all()

    hobbies_map: dict[int, list[Hobby]] = {uid: [] for uid in user_ids}
    for uid, hobby in hobbies_rows:
        hobbies_map[uid].append(Hobby(hobby))

    profiles = [
        ProfileOut(
            user_id=r["user_id"],
            display_name=r["display_name"],
            bio=r["bio"],
            birth_date=r["birth_date"],
            city=r["city"],
            gender=r["gender"],
            height_cm=r["height_cm"],
            hobbies=hobbies_map[r["user_id"]],
            updated_at=r["updated_at"],
        )
        for r in rows
    ]
    return DiscoveryBatch(profiles=profiles)
