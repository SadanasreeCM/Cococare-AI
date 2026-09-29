"""
Phase 3 API Routes — Expense Tracker, Farm Blocks & Growth Tracker.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.database import get_db
from backend.models import Farm, Expense, FarmBlock, GrowthRecord
from backend.schemas import (
    ExpenseCreate, ExpenseResponse, ExpenseSummaryResponse,
    FarmBlockCreate, FarmBlockResponse,
    GrowthRecordCreate, GrowthRecordResponse
)
from backend.constants import EXPENSE_CATEGORIES, PALM_VARIETIES

router = APIRouter(prefix="/api", tags=["Phase 3 — Finance & Growth"])


# ---------------------------------------------------------------------------
# 1. Expense Tracker Routes
# ---------------------------------------------------------------------------
@router.post("/expenses", response_model=ExpenseResponse)
def create_expense(req: ExpenseCreate, db: Session = Depends(get_db)):
    """Record a farm expense."""
    farm = db.query(Farm).filter(Farm.id == req.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    if req.category not in EXPENSE_CATEGORIES:
        req.category = "Miscellaneous Farm Overhead"

    exp = Expense(**req.model_dump())
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.get("/expenses/farm/{farm_id}", response_model=List[ExpenseResponse])
def get_expenses_history(farm_id: int, db: Session = Depends(get_db)):
    """Fetch expense history for a farm."""
    return db.query(Expense).filter(
        Expense.farm_id == farm_id
    ).order_by(Expense.date.desc()).all()


@router.get("/expenses/summary/farm/{farm_id}", response_model=ExpenseSummaryResponse)
def get_expense_summary(farm_id: int, db: Session = Depends(get_db)):
    """Compute total investment, monthly expenses, and category breakdown."""
    expenses = db.query(Expense).filter(Expense.farm_id == farm_id).all()

    total = sum(e.amount for e in expenses)

    current_month_str = datetime.utcnow().strftime("%Y-%m")
    monthly = sum(e.amount for e in expenses if e.date.startswith(current_month_str))

    breakdown: Dict[str, float] = {}
    for cat in EXPENSE_CATEGORIES:
        breakdown[cat] = 0.0

    for e in expenses:
        cat = e.category if e.category in breakdown else "Miscellaneous Farm Overhead"
        breakdown[cat] += e.amount

    return ExpenseSummaryResponse(
        total_investment=total,
        monthly_expense=monthly,
        category_breakdown=breakdown,
        expense_count=len(expenses)
    )


@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense record."""
    exp = db.query(Expense).filter(Expense.id == expense_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(exp)
    db.commit()
    return {"success": True, "message": "Expense deleted", "deleted_id": expense_id}


# ---------------------------------------------------------------------------
# 2. Growth & Farm Block Tracker Routes
# ---------------------------------------------------------------------------
@router.post("/blocks", response_model=FarmBlockResponse)
def create_farm_block(req: FarmBlockCreate, db: Session = Depends(get_db)):
    """Create a new plantation block."""
    farm = db.query(Farm).filter(Farm.id == req.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    block = FarmBlock(**req.model_dump())
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


@router.get("/blocks/farm/{farm_id}", response_model=List[FarmBlockResponse])
def get_farm_blocks(farm_id: int, db: Session = Depends(get_db)):
    """Fetch all blocks for a farm."""
    return db.query(FarmBlock).filter(
        FarmBlock.farm_id == farm_id
    ).order_by(FarmBlock.created_at.asc()).all()


@router.post("/growth", response_model=GrowthRecordResponse)
def log_growth_record(req: GrowthRecordCreate, db: Session = Depends(get_db)):
    """Log a growth observation or yield record for a block."""
    block = db.query(FarmBlock).filter(FarmBlock.id == req.block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Farm block not found")

    rec = GrowthRecord(**req.model_dump())
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/growth/block/{block_id}", response_model=List[GrowthRecordResponse])
def get_block_growth_timeline(block_id: int, db: Session = Depends(get_db)):
    """Fetch growth timeline for a specific block."""
    return db.query(GrowthRecord).filter(
        GrowthRecord.block_id == block_id
    ).order_by(GrowthRecord.date.desc()).all()
