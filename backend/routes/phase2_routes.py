"""
Phase 2 API Routes — Irrigation, Soil Management, Fertilizer Calendar & Farm Calendar.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import Farm, IrrigationRecord, SoilTest, FarmActivity
from backend.schemas import (
    IrrigationCreate, IrrigationResponse,
    SoilTestCreate, SoilTestResponse,
    FarmActivityCreate, FarmActivityResponse
)
from backend.constants import SOIL_RANGE_THRESHOLDS, FERTILIZER_RECOMMENDATIONS_BY_AGE

router = APIRouter(prefix="/api", tags=["Phase 2 — Operations"])


# ---------------------------------------------------------------------------
# 1. Irrigation Planner Routes
# ---------------------------------------------------------------------------
@router.post("/irrigation", response_model=IrrigationResponse)
def create_irrigation_record(req: IrrigationCreate, db: Session = Depends(get_db)):
    """Log an irrigation event or scheduled reminder."""
    farm = db.query(Farm).filter(Farm.id == req.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    rec = IrrigationRecord(**req.model_dump())
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/irrigation/farm/{farm_id}", response_model=List[IrrigationResponse])
def get_irrigation_history(farm_id: int, db: Session = Depends(get_db)):
    """Fetch all irrigation records for a farm."""
    return db.query(IrrigationRecord).filter(
        IrrigationRecord.farm_id == farm_id
    ).order_by(IrrigationRecord.date.desc()).all()


@router.patch("/irrigation/{record_id}/status", response_model=IrrigationResponse)
def update_irrigation_status(record_id: int, status: str = "COMPLETED", db: Session = Depends(get_db)):
    """Mark an irrigation task as COMPLETED or PENDING."""
    rec = db.query(IrrigationRecord).filter(IrrigationRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Irrigation record not found")

    rec.status = status
    db.commit()
    db.refresh(rec)
    return rec


# ---------------------------------------------------------------------------
# 2. Soil Management Routes
# ---------------------------------------------------------------------------
@router.post("/soil", response_model=SoilTestResponse)
def create_soil_test(req: SoilTestCreate, db: Session = Depends(get_db)):
    """Log a soil test result."""
    farm = db.query(Farm).filter(Farm.id == req.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    test = SoilTest(**req.model_dump())
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


@router.get("/soil/farm/{farm_id}", response_model=List[SoilTestResponse])
def get_soil_test_history(farm_id: int, db: Session = Depends(get_db)):
    """Fetch soil test history for a farm."""
    return db.query(SoilTest).filter(
        SoilTest.farm_id == farm_id
    ).order_by(SoilTest.date.desc()).all()


@router.get("/soil/interpretation")
def get_soil_interpretations(ph: float = 6.5, n: float = 180.0, p: float = 18.0, k: float = 220.0, oc: float = 0.75):
    """Return static defensible evaluation of soil parameters based on standard agronomic ranges."""
    results = {}
    vals = {"ph": ph, "nitrogen": n, "phosphorus": p, "potassium": k, "organic_carbon": oc}
    
    for key, spec in SOIL_RANGE_THRESHOLDS.items():
        v = vals.get(key, 0.0)
        results[key] = {
            "label": spec["label"],
            "value": v,
            "unit": spec["unit"],
            "optimal_range": spec["optimal_range"],
            "evaluation": spec["evaluator"](v),
            "status_color": spec["status_color"](v),
            "reference": spec["reference"]
        }
    return results


# ---------------------------------------------------------------------------
# 3. Fertilizer & Nutrient Calendar Routes
# ---------------------------------------------------------------------------
@router.get("/fertilizer/templates")
def get_fertilizer_templates():
    """Return static recommended fertilizer activities grouped by tree age bracket."""
    return FERTILIZER_RECOMMENDATIONS_BY_AGE


# ---------------------------------------------------------------------------
# 4. Integrated Farm Calendar Routes
# ---------------------------------------------------------------------------
@router.get("/calendar/farm/{farm_id}", response_model=List[FarmActivityResponse])
def get_farm_calendar(farm_id: int, db: Session = Depends(get_db)):
    """Get all scheduled & completed activities for a farm."""
    return db.query(FarmActivity).filter(
        FarmActivity.farm_id == farm_id
    ).order_by(FarmActivity.scheduled_date.asc()).all()


@router.post("/calendar", response_model=FarmActivityResponse)
def create_farm_activity(req: FarmActivityCreate, db: Session = Depends(get_db)):
    """Add a custom activity to the farm calendar."""
    farm = db.query(Farm).filter(Farm.id == req.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    act = FarmActivity(**req.model_dump())
    db.add(act)
    db.commit()
    db.refresh(act)
    return act


@router.patch("/calendar/{activity_id}/status", response_model=FarmActivityResponse)
def toggle_activity_status(activity_id: int, status: str = "COMPLETED", db: Session = Depends(get_db)):
    """Mark a calendar activity as COMPLETED or PENDING."""
    act = db.query(FarmActivity).filter(FarmActivity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")

    act.status = status
    if status == "COMPLETED":
        act.completed_at = datetime.utcnow().strftime("%Y-%m-%d")
    else:
        act.completed_at = None

    db.commit()
    db.refresh(act)
    return act
