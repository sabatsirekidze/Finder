from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import StatsOut

router = APIRouter()

_WINDOW = "NOW() - INTERVAL '30 days'"


@router.get("/me", response_model=StatsOut)
def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    me = current_user.id

    total_swipes = db.execute(
        text(f"SELECT COUNT(*) FROM swipes WHERE swiper_user_id = :me AND created_at >= {_WINDOW}"),
        {"me": me},
    ).scalar()

    smashes_received = db.execute(
        text(
            f"SELECT COUNT(*) FROM swipes "
            f"WHERE target_user_id = :me AND direction = 'smash' AND created_at >= {_WINDOW}"
        ),
        {"me": me},
    ).scalar()

    total_matches = db.execute(
        text(
            f"SELECT COUNT(*) FROM matches "
            f"WHERE (user_low_id = :me OR user_high_id = :me) AND created_at >= {_WINDOW}"
        ),
        {"me": me},
    ).scalar()

    avg_messages = db.execute(
        text(f"""
            SELECT AVG(msg_count) FROM (
                SELECT m.id, COUNT(msg.id) AS msg_count
                FROM matches m
                JOIN messages msg ON msg.match_id = m.id
                WHERE (m.user_low_id = :me OR m.user_high_id = :me)
                  AND msg.created_at >= {_WINDOW}
                GROUP BY m.id
            ) sub
        """),
        {"me": me},
    ).scalar()

    return StatsOut(
        total_swipes_made=total_swipes or 0,
        smashes_received=smashes_received or 0,
        total_matches=total_matches or 0,
        avg_messages_per_match=float(avg_messages) if avg_messages is not None else None,
    )
