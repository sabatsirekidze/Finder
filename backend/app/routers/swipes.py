from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.enums import SwipeDirection
from app.models import Match, Swipe, User
from app.schemas import SwipeRequest, SwipeResult

router = APIRouter()


@router.post("", response_model=SwipeResult, status_code=201)
def create_swipe(
    body: SwipeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.target_user_id == current_user.id:
        raise HTTPException(400, "Cannot swipe on yourself")

    swipe = Swipe(
        swiper_user_id=current_user.id,
        target_user_id=body.target_user_id,
        direction=body.direction,
    )
    db.add(swipe)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Already swiped on this user")

    match_id: int | None = None
    match_created = False

    if body.direction == SwipeDirection.SMASH:
        reciprocal = db.execute(
            text(
                "SELECT 1 FROM swipes "
                "WHERE swiper_user_id = :target AND target_user_id = :me "
                "AND direction = 'smash'"
            ),
            {"target": body.target_user_id, "me": current_user.id},
        ).first()

        if reciprocal:
            low, high = sorted([current_user.id, body.target_user_id])
            existing = db.execute(
                text("SELECT id FROM matches WHERE user_low_id = :low AND user_high_id = :high"),
                {"low": low, "high": high},
            ).first()
            if not existing:
                match = Match(user_low_id=low, user_high_id=high)
                db.add(match)
                db.flush()
                match_id = match.id
                match_created = True

    db.commit()
    return SwipeResult(swipe_id=swipe.id, match_created=match_created, match_id=match_id)
