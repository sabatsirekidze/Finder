from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import Match, Message, User
from app.schemas import MessageOut, MessageRequest

router = APIRouter()


def _get_match_or_403(match_id: int, user_id: int, db: Session) -> Match:
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(404, "Match not found")
    if user_id not in (match.user_low_id, match.user_high_id):
        raise HTTPException(403, "Not a participant of this match")
    return match


@router.get("/matches/{match_id}/messages", response_model=list[MessageOut])
def list_messages(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_match_or_403(match_id, current_user.id, db)
    return (
        db.query(Message)
        .filter_by(match_id=match_id)
        .order_by(Message.created_at)
        .all()
    )


@router.post("/matches/{match_id}/messages", response_model=MessageOut, status_code=201)
def send_message(
    match_id: int,
    body: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_match_or_403(match_id, current_user.id, db)
    if not body.body.strip():
        raise HTTPException(400, "Message body cannot be empty")
    msg = Message(match_id=match_id, sender_user_id=current_user.id, body=body.body)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
