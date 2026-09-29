"""
Farm management routes — Farm Setup, Profile & Configuration.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models import Farm, User
from backend.schemas import FarmCreate, FarmUpdate, FarmResponse
from backend.constants import SOIL_TYPES

router = APIRouter(prefix="/api", tags=["Farm"])


@router.post("/farm", response_model=FarmResponse)
@router.post("/farm/", response_model=FarmResponse)
def create_or_replace_farm(req: FarmCreate, db: Session = Depends(get_db)):
    """Create a new farm profile for a user, or replace existing if present."""
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        # If user 1 doesn't exist yet, auto-create default user
        if req.user_id == 1 or not db.query(User).first():
            user = User(
                username="default_farmer",
                password_hash="8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",
                preferred_language="en"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            req.user_id = user.id
        else:
            raise HTTPException(status_code=404, detail="User not found")

    if req.soil_type not in SOIL_TYPES:
        req.soil_type = "loamy"

    existing_farm = db.query(Farm).filter(Farm.user_id == req.user_id).first()
    if existing_farm:
        # Update existing
        for field, val in req.model_dump().items():
            if field != "user_id" and val is not None:
                setattr(existing_farm, field, val)
        db.commit()
        db.refresh(existing_farm)
        return existing_farm

    farm = Farm(**req.model_dump())
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get("/farm/user/{user_id}", response_model=FarmResponse)
def get_farm_by_user(user_id: int, db: Session = Depends(get_db)):
    """Get farm details for a given user."""
    farm = db.query(Farm).filter(Farm.user_id == user_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm profile not found for user")
    return farm


@router.put("/farm/{farm_id}", response_model=FarmResponse)
def update_farm(farm_id: int, req: FarmUpdate, db: Session = Depends(get_db)):
    """Update specific farm profile details."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    update_data = req.model_dump(exclude_unset=True)
    if "soil_type" in update_data and update_data["soil_type"] not in SOIL_TYPES:
        update_data["soil_type"] = "loamy"

    for field, val in update_data.items():
        setattr(farm, field, val)

    db.commit()
    db.refresh(farm)
    return farm
