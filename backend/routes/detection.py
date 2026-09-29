from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.detection_service import process_detection

router = APIRouter(prefix="/api", tags=["Detection"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_MB = 15

@router.post("/detect")
async def detect_disease(
    file: UploadFile = File(...),
    confidence: float = Query(0.5, ge=0.1, le=1.0, description="Confidence threshold between 0.1 and 1.0"),
    language: str = Query("en", description="Language code: en, ta, hi"),
    db: Session = Depends(get_db)
):
    """
    Accepts an uploaded image file of a coconut tree/leaf, runs Roboflow object detection,
    annotates bounding boxes, saves detection history to SQLite, and returns detailed predictions
    with localized disease description and treatment recommendation.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a valid filename.")

    ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension '{ext}'. Allowed extensions are JPG, JPEG, PNG, WEBP."
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE_MB}MB."
        )

    try:
        result = process_detection(
            db=db,
            filename=file.filename,
            image_bytes=content,
            confidence_threshold=confidence,
            language=language
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")
