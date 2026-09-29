"""
Auth routes — Minimal user signup/login with language preference persistence.

Uses SQLite-backed User model.  Passwords are hashed with bcrypt.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.chatbot import SUPPORTED_LANGUAGES

import hashlib

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class SignupRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4)
    preferred_language: str = Field("en")


class LoginRequest(BaseModel):
    username: str
    password: str


class LanguageUpdateRequest(BaseModel):
    preferred_language: str = Field(..., description="Language code: en, ta, hi")


class UserResponse(BaseModel):
    id: int
    username: str
    preferred_language: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _hash_password(password: str) -> str:
    """Simple SHA-256 hash for demo purposes."""
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/signup", response_model=UserResponse)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user with optional language preference."""
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    lang = req.preferred_language if req.preferred_language in SUPPORTED_LANGUAGES else "en"

    user = User(
        username=req.username,
        password_hash=_hash_password(req.password),
        preferred_language=lang,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(id=user.id, username=user.username, preferred_language=user.preferred_language)


@router.post("/login", response_model=UserResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return profile (including preferred language)."""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or user.password_hash != _hash_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return UserResponse(id=user.id, username=user.username, preferred_language=user.preferred_language)


@router.get("/me/{user_id}", response_model=UserResponse)
def get_me(user_id: int, db: Session = Depends(get_db)):
    """Fetch current user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(id=user.id, username=user.username, preferred_language=user.preferred_language)


@router.patch("/language", response_model=UserResponse)
def update_language(req: LanguageUpdateRequest, user_id: int, db: Session = Depends(get_db)):
    """Update user's preferred language. Language preference persists across sessions."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if req.preferred_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Choose from: {SUPPORTED_LANGUAGES}"
        )

    user.preferred_language = req.preferred_language
    db.commit()
    db.refresh(user)

    return UserResponse(id=user.id, username=user.username, preferred_language=user.preferred_language)
