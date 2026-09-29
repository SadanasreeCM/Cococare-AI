import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.config import settings
from backend.database import get_db
from backend.models import Detection, DetectionResult
from backend.disease_info import get_disease_info
from backend.schemas import HistoryItem, HistoryDetailResponse, DeleteResponse, LinkDetectionRequest

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("", response_model=List[HistoryItem])
def get_history(
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve list of previous coconut tree disease detection scans."""
    query = db.query(Detection)

    if status_filter and status_filter.lower() != "all":
        query = query.filter(Detection.status.ilike(f"%{status_filter}%"))

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (Detection.filename.ilike(term)) |
            (Detection.primary_disease.ilike(term))
        )

    records = query.order_by(desc(Detection.timestamp)).limit(limit).all()

    items = []
    for r in records:
        blk_name = r.block.block_name if r.block else None
        items.append(HistoryItem(
            id=r.id,
            filename=r.filename,
            timestamp=r.timestamp,
            status=r.status,
            total_detections=r.total_detections,
            primary_disease=r.primary_disease,
            max_confidence=r.max_confidence,
            confidence_threshold=r.confidence_threshold,
            original_image_url=f"{settings.BACKEND_URL}{r.original_image_path}",
            annotated_image_url=f"{settings.BACKEND_URL}{r.annotated_image_path}",
            block_id=r.block_id,
            farmer_notes=r.farmer_notes,
            block_name=blk_name
        ))

    return items

@router.get("/{detection_id}", response_model=HistoryDetailResponse)
def get_history_detail(detection_id: int, db: Session = Depends(get_db)):
    """Retrieve complete detection record including bounding boxes and disease details."""
    r = db.query(Detection).filter(Detection.id == detection_id).first()
    if not r:
        raise HTTPException(status_code=404, detail=f"Detection record {detection_id} not found.")

    detections = []
    detected_classes = set()
    for res in r.results:
        detected_classes.add(res.class_name)
        detections.append({
            "class_name": res.class_name,
            "confidence": res.confidence,
            "x": res.x,
            "y": res.y,
            "width": res.width,
            "height": res.height,
            "severity": res.severity
        })

    disease_details = {}
    if not detected_classes:
        detected_classes = {r.primary_disease}
    for cls in detected_classes:
        disease_details[cls] = get_disease_info(cls)

    blk_name = r.block.block_name if r.block else None

    return HistoryDetailResponse(
        id=r.id,
        filename=r.filename,
        timestamp=r.timestamp,
        status=r.status,
        total_detections=r.total_detections,
        primary_disease=r.primary_disease,
        max_confidence=r.max_confidence,
        confidence_threshold=r.confidence_threshold,
        original_image_url=f"{settings.BACKEND_URL}{r.original_image_path}",
        annotated_image_url=f"{settings.BACKEND_URL}{r.annotated_image_path}",
        detections=detections,
        disease_details=disease_details,
        block_id=r.block_id,
        farmer_notes=r.farmer_notes,
        block_name=blk_name
    )

@router.patch("/{detection_id}/link", response_model=HistoryItem)
def link_detection_to_block(detection_id: int, req: LinkDetectionRequest, db: Session = Depends(get_db)):
    """Link a disease scan to a farm block and record farmer diagnosis notes."""
    r = db.query(Detection).filter(Detection.id == detection_id).first()
    if not r:
        raise HTTPException(status_code=404, detail=f"Detection record {detection_id} not found.")

    if req.block_id is not None:
        r.block_id = req.block_id
    if req.farmer_notes is not None:
        r.farmer_notes = req.farmer_notes

    db.commit()
    db.refresh(r)

    blk_name = r.block.block_name if r.block else None
    return HistoryItem(
        id=r.id,
        filename=r.filename,
        timestamp=r.timestamp,
        status=r.status,
        total_detections=r.total_detections,
        primary_disease=r.primary_disease,
        max_confidence=r.max_confidence,
        confidence_threshold=r.confidence_threshold,
        original_image_url=f"{settings.BACKEND_URL}{r.original_image_path}",
        annotated_image_url=f"{settings.BACKEND_URL}{r.annotated_image_path}",
        block_id=r.block_id,
        farmer_notes=r.farmer_notes,
        block_name=blk_name
    )

@router.delete("/clear-all", response_model=DeleteResponse)
def clear_all_history(db: Session = Depends(get_db)):
    """Clear all history records and delete image files."""
    records = db.query(Detection).all()
    count = len(records)
    for r in records:
        for rel_path in [r.original_image_path, r.annotated_image_path]:
            if rel_path and rel_path.startswith("/uploads/"):
                abs_p = os.path.join(settings.UPLOADS_DIR, rel_path.replace("/uploads/", ""))
                if os.path.exists(abs_p):
                    try:
                        os.remove(abs_p)
                    except Exception:
                        pass
        db.delete(r)

    db.commit()
    return DeleteResponse(success=True, message=f"Successfully cleared {count} detection records.")

@router.delete("/{detection_id}", response_model=DeleteResponse)
def delete_history_item(detection_id: int, db: Session = Depends(get_db)):
    """Delete a single detection record and its image files."""
    r = db.query(Detection).filter(Detection.id == detection_id).first()
    if not r:
        raise HTTPException(status_code=404, detail=f"Detection record {detection_id} not found.")

    for rel_path in [r.original_image_path, r.annotated_image_path]:
        if rel_path and rel_path.startswith("/uploads/"):
            abs_p = os.path.join(settings.UPLOADS_DIR, rel_path.replace("/uploads/", ""))
            if os.path.exists(abs_p):
                try:
                    os.remove(abs_p)
                except Exception:
                    pass

    db.delete(r)
    db.commit()

    return DeleteResponse(success=True, message=f"Deleted detection record {detection_id}.", deleted_id=detection_id)

