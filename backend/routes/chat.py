"""
Chat API route — Proxies user messages to the Groq chatbot with language support.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Farm, Detection
from backend.chatbot import get_chat_response, SUPPORTED_LANGUAGES

router = APIRouter(prefix="/api", tags=["Chat"])


class ChatRequest(BaseModel):
    message: Optional[str] = Field(None, description="User message text")
    user_message: Optional[str] = Field(None, description="User message text alias")
    language: str = Field("en", description="Language code: en, ta, hi")
    history: Optional[List[Dict]] = Field(None, description="Prior conversation turns")
    chat_history: Optional[List[Dict]] = Field(None, description="Prior conversation turns alias")
    user_context: Optional[str] = Field(None, description="Last scan result or context string")
    user_id: int = Field(1, description="User ID for farm context lookups")


class ChatResponse(BaseModel):
    success: bool
    reply: str
    language: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    """Send a message to the CoconutCare Groq-powered chatbot and receive a response."""
    language = req.language if req.language in SUPPORTED_LANGUAGES else "en"
    msg = req.user_message or req.message or ""
    if not msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    hist = req.chat_history if req.chat_history is not None else req.history

    # Build contextual background from DB
    context_parts = []
    if req.user_context:
        context_parts.append(req.user_context)

    # Fetch farm profile if available
    farm = db.query(Farm).filter(Farm.user_id == req.user_id).first()
    if farm:
        context_parts.append(
            f"Farm Profile Context: Name={farm.name}, Location={farm.location}, Size={farm.land_area} {farm.land_unit}, "
            f"Trees={farm.existing_trees}, Soil={farm.soil_type}, Irrigation={farm.irrigation_method}."
        )

    
    # Fetch recent disease detections (last 3)
    recent_scans = db.query(Detection).order_by(Detection.timestamp.desc()).limit(3).all()
    if recent_scans:
        scan_summaries = [f"{s.primary_disease} ({s.max_confidence*100:.0f}% on {s.timestamp.strftime('%Y-%m-%d') if s.timestamp else 'recent'})" for s in recent_scans]
        context_parts.append(f"Recent Disease Scans on Farm: {', '.join(scan_summaries)}.")

    full_context = "\n".join(context_parts) if context_parts else None

    try:
        reply = get_chat_response(
            user_message=msg,
            chat_history=hist,
            user_context=full_context,
            language=language,
        )
        return ChatResponse(success=True, reply=reply, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

