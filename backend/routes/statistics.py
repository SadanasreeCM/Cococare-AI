from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.database import get_db
from backend.models import Detection
from backend.schemas import StatisticsResponse, DiseaseCountItem

router = APIRouter(prefix="/api", tags=["Statistics"])

@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    """Calculates live analytics statistics from the SQLite database."""
    total_scans = db.query(func.count(Detection.id)).scalar() or 0

    if total_scans == 0:
        return StatisticsResponse(
            total_scans=0,
            healthy_scans=0,
            diseased_scans=0,
            healthy_percentage=0.0,
            diseased_percentage=0.0,
            most_common_disease="N/A",
            average_confidence=0.0,
            disease_distribution=[],
            latest_scan_timestamp=None
        )

    healthy_scans = db.query(func.count(Detection.id)).filter(Detection.status == "Healthy").scalar() or 0
    diseased_scans = db.query(func.count(Detection.id)).filter(Detection.status != "Healthy").scalar() or 0

    healthy_percentage = round((healthy_scans / total_scans) * 100, 1)
    diseased_percentage = round((diseased_scans / total_scans) * 100, 1)

    avg_conf = db.query(func.avg(Detection.max_confidence)).scalar() or 0.0
    average_confidence = round(float(avg_conf) * 100, 1)

    # Disease distribution
    distribution_query = (
        db.query(Detection.primary_disease, func.count(Detection.id).label("cnt"))
        .group_by(Detection.primary_disease)
        .order_by(desc("cnt"))
        .all()
    )

    disease_distribution = [
        DiseaseCountItem(disease_name=row[0], count=row[1])
        for row in distribution_query
    ]

    most_common = disease_distribution[0].disease_name if disease_distribution else "Healthy"

    latest_rec = db.query(Detection.timestamp).order_by(desc(Detection.timestamp)).first()
    latest_scan_timestamp = latest_rec[0] if latest_rec else None

    return StatisticsResponse(
        total_scans=total_scans,
        healthy_scans=healthy_scans,
        diseased_scans=diseased_scans,
        healthy_percentage=healthy_percentage,
        diseased_percentage=diseased_percentage,
        most_common_disease=most_common,
        average_confidence=average_confidence,
        disease_distribution=disease_distribution,
        latest_scan_timestamp=latest_scan_timestamp
    )
