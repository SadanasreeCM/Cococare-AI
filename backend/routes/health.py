from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.config import settings
from backend.database import get_db
from backend.schemas import HealthResponse
from backend.roboflow_service import roboflow_service

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    """Check API service health, database connection, and Roboflow configuration."""
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        roboflow_configured=roboflow_service.is_configured(),
        database_connected=db_ok
    )
