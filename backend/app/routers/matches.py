from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import Match, Profile, User
from app.schemas import MatchOut

router = APIRouter()


@router.get("", response_model=list[MatchOut])
def list_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    matches = (
        db.query(Match)
        .filter(
            or_(Match.user_low_id == current_user.id, Match.user_high_id == current_user.id)
        )
        .order_by(Match.created_at.desc())
        .all()
    )

    result = []
    for m in matches:
        other_id = m.user_high_id if m.user_low_id == current_user.id else m.user_low_id
        other_profile = db.get(Profile, other_id)
        result.append(
            MatchOut(
                id=m.id,
                other_user_id=other_id,
                other_display_name=other_profile.display_name if other_profile else None,
                created_at=m.created_at,
            )
        )
    return result
