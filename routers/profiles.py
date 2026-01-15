from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models import (
    User, UserProfile, UserPersonalEmail, UserDependent,
    Country, City, EducationLevel
)
from schemas import (
    UserProfileOut, UserProfileIn,
    CountryOut, CityOut, EducationLevelOut
)
from db import get_session
from auth.deps import get_current_user

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])

# --- Reference Data ---

@router.get("/countries", response_model=list[CountryOut])
def list_countries(session: Session = Depends(get_session)):
    return session.exec(select(Country).order_by(Country.name)).all()

@router.get("/cities/{country_id}", response_model=list[CityOut])
def list_cities(country_id: int, session: Session = Depends(get_session)):
    return session.exec(select(City).where(City.country_id == country_id).order_by(City.name)).all()

@router.get("/education-levels", response_model=list[EducationLevelOut])
def list_education_levels(session: Session = Depends(get_session)):
    return session.exec(select(EducationLevel).order_by(EducationLevel.id)).all()

# --- Profile Management ---

@router.get("/me", response_model=UserProfileOut)
def get_my_profile(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    profile = session.get(UserProfile, user.id)
    if not profile:
        # Create empty profile if none exists
        profile = UserProfile(user_id=user.id)
        session.add(profile)
        session.commit()
        session.refresh(profile)
    return profile

@router.put("/me", response_model=UserProfileOut)
def update_my_profile(
    profile_in: UserProfileIn,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    profile = session.get(UserProfile, user.id)
    if not profile:
        profile = UserProfile(user_id=user.id)
        session.add(profile)
    
    # Update fields
    data = profile_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(profile, key, value)
    
    profile.updated_at = datetime.utcnow()
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

import shutil
import os
from fastapi import UploadFile, File

@router.post("/avatar", response_model=UserProfileOut)
def upload_avatar(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    profile = session.get(UserProfile, user.id)
    if not profile:
        profile = UserProfile(user_id=user.id)
        session.add(profile)
    
    # Ensure directory exists
    os.makedirs("static/uploads", exist_ok=True)
    
    # Save file
    safe_filename = f"user_{user.id}_{file.filename}"
    file_path = f"static/uploads/{safe_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Construct URL (assuming mounting at /static)
    # Ideally use a base_url from env or request, but relative path works for frontend often if proxied.
    # Or absolute path if we know the domain. For now, /static/...
    profile.profile_picture_url = f"/api/static/uploads/{safe_filename}"
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

# --- Dependents Management ---

from schemas import UserDependentOut, UserDependentIn

@router.get("/dependents", response_model=list[UserDependentOut])
def list_my_dependents(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return session.exec(select(UserDependent).where(UserDependent.user_id == user.id)).all()

@router.post("/dependents", response_model=UserDependentOut)
def add_dependent(
    dependent_in: UserDependentIn,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    dependent = UserDependent.model_validate(dependent_in, update={"user_id": user.id})
    session.add(dependent)
    session.commit()
    session.refresh(dependent)
    return dependent

@router.delete("/dependents/{dependent_id}")
def delete_dependent(
    dependent_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    dependent = session.get(UserDependent, dependent_id)
    if not dependent or dependent.user_id != user.id:
        raise HTTPException(status_code=404, detail="Dependent not found")
    
    session.delete(dependent)
    session.commit()
    return {"status": "ok"}
