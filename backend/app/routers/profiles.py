from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import (
    DatingPreferenceGender,
    DatingPreferenceHobby,
    DatingPreferences,
    Profile,
    ProfileHobby,
    User,
)
from app.schemas import (
    DatingPreferencesOut,
    DatingPreferencesUpdateRequest,
    ProfileOut,
    ProfileUpdateRequest,
)

router = APIRouter()


def _profile_out(profile: Profile, db: Session) -> ProfileOut:
    hobbies = [ph.hobby for ph in db.query(ProfileHobby).filter_by(user_id=profile.user_id).all()]
    return ProfileOut(
        user_id=profile.user_id,
        display_name=profile.display_name,
        bio=profile.bio,
        birth_date=profile.birth_date,
        city=profile.city,
        gender=profile.gender,
        height_cm=profile.height_cm,
        hobbies=hobbies,
        updated_at=profile.updated_at,
    )


@router.get("/me", response_model=ProfileOut)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.get(Profile, current_user.id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return _profile_out(profile, db)


@router.patch("/me", response_model=ProfileOut)
def update_my_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.get(Profile, current_user.id)
    if not profile:
        raise HTTPException(404, "Profile not found")

    if body.display_name is not None:
        profile.display_name = body.display_name
    if body.bio is not None:
        profile.bio = body.bio
    if body.birth_date is not None:
        profile.birth_date = body.birth_date
    if body.city is not None:
        profile.city = body.city
    if body.gender is not None:
        profile.gender = body.gender
    if body.height_cm is not None:
        profile.height_cm = body.height_cm

    if body.hobbies is not None:
        db.query(ProfileHobby).filter_by(user_id=current_user.id).delete()
        for h in body.hobbies:
            db.add(ProfileHobby(user_id=current_user.id, hobby=h))

    profile.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(profile)
    return _profile_out(profile, db)


@router.get("/me/preferences", response_model=DatingPreferencesOut)
def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prefs = db.get(DatingPreferences, current_user.id)
    if not prefs:
        raise HTTPException(404, "Preferences not found")
    return DatingPreferencesOut(
        partner_age_min=prefs.partner_age_min,
        partner_age_max=prefs.partner_age_max,
        prefer_same_city=prefs.prefer_same_city,
        partner_genders=[g.gender for g in prefs.partner_genders],
        partner_hobbies=[h.hobby for h in prefs.partner_hobbies],
    )


@router.patch("/me/preferences", response_model=DatingPreferencesOut)
def update_my_preferences(
    body: DatingPreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prefs = db.get(DatingPreferences, current_user.id)
    if not prefs:
        raise HTTPException(404, "Preferences not found")

    if body.partner_age_min is not None:
        prefs.partner_age_min = body.partner_age_min
    if body.partner_age_max is not None:
        prefs.partner_age_max = body.partner_age_max
    if body.prefer_same_city is not None:
        prefs.prefer_same_city = body.prefer_same_city

    if body.partner_genders is not None:
        db.query(DatingPreferenceGender).filter_by(user_id=current_user.id).delete()
        for g in body.partner_genders:
            db.add(DatingPreferenceGender(user_id=current_user.id, gender=g))

    if body.partner_hobbies is not None:
        db.query(DatingPreferenceHobby).filter_by(user_id=current_user.id).delete()
        for h in body.partner_hobbies:
            db.add(DatingPreferenceHobby(user_id=current_user.id, hobby=h))

    db.commit()
    db.refresh(prefs)
    return DatingPreferencesOut(
        partner_age_min=prefs.partner_age_min,
        partner_age_max=prefs.partner_age_max,
        prefer_same_city=prefs.prefer_same_city,
        partner_genders=[g.gender for g in prefs.partner_genders],
        partner_hobbies=[h.hobby for h in prefs.partner_hobbies],
    )
