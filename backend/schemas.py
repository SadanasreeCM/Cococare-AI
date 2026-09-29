from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    roboflow_configured: bool
    database_connected: bool

class DetectionItem(BaseModel):
    class_name: str = Field(..., description="Name of detected disease or condition")
    confidence: float = Field(..., description="Detection confidence score between 0 and 1")
    x: float = Field(..., description="Center X coordinate")
    y: float = Field(..., description="Center Y coordinate")
    width: float = Field(..., description="Bounding box width")
    height: float = Field(..., description="Bounding box height")
    severity: str = Field("Low", description="Severity category: High, Medium, Low")

class DiseaseInfoSchema(BaseModel):
    display_name: str
    scientific_name: str
    severity: str
    severity_color: str
    description: str
    symptoms: List[str]
    causes: List[str]
    recommended_action: List[str]
    prevention: List[str]

class DetectionResponse(BaseModel):
    success: bool
    detection_id: int
    filename: str
    timestamp: datetime
    status: str # Healthy, Diseased, Warning
    total_detections: int
    primary_disease: str
    max_confidence: float
    confidence_threshold: float
    original_image_url: str
    annotated_image_url: str
    detections: List[DetectionItem]
    disease_details: Dict[str, DiseaseInfoSchema]
    block_id: Optional[int] = None
    farmer_notes: Optional[str] = None

class HistoryItem(BaseModel):
    id: int
    filename: str
    timestamp: datetime
    status: str
    total_detections: int
    primary_disease: str
    max_confidence: float
    confidence_threshold: float
    original_image_url: str
    annotated_image_url: str
    block_id: Optional[int] = None
    farmer_notes: Optional[str] = None
    block_name: Optional[str] = None

class HistoryDetailResponse(HistoryItem):
    detections: List[DetectionItem]
    disease_details: Dict[str, DiseaseInfoSchema]

class LinkDetectionRequest(BaseModel):
    block_id: Optional[int] = Field(None, description="Farm block ID to link")
    farmer_notes: Optional[str] = Field(None, description="Farmer diagnosis notes")


class DiseaseCountItem(BaseModel):
    disease_name: str
    count: int

class StatisticsResponse(BaseModel):
    total_scans: int
    healthy_scans: int
    diseased_scans: int
    healthy_percentage: float
    diseased_percentage: float
    most_common_disease: str
    average_confidence: float
    disease_distribution: List[DiseaseCountItem]
    latest_scan_timestamp: Optional[datetime] = None

class DeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_id: Optional[int] = None

class FarmBase(BaseModel):
    name: str = Field(..., description="Farm name")
    location: str = Field(..., description="Location/Region")
    land_area: float = Field(..., gt=0, description="Total land area")
    land_unit: str = Field("acres", description="acres or hectares")
    soil_type: str = Field("loamy", description="sandy, loamy, clayey, red, laterite")
    water_source: Optional[str] = Field("Borewell", description="Water source")
    irrigation_method: Optional[str] = Field("Drip", description="Irrigation method")
    existing_trees: int = Field(0, ge=0, description="Number of existing trees")
    planting_date: Optional[str] = Field(None, description="Planting date YYYY-MM-DD")
    soil_test_info: Optional[str] = Field(None, description="Optional soil test notes")

class FarmCreate(FarmBase):
    user_id: int

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    land_area: Optional[float] = None
    land_unit: Optional[str] = None
    soil_type: Optional[str] = None
    water_source: Optional[str] = None
    irrigation_method: Optional[str] = None
    existing_trees: Optional[int] = None
    planting_date: Optional[str] = None
    soil_test_info: Optional[str] = None

class FarmResponse(FarmBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------------------------------------------------------------------------
# Phase 2 Schemas — Irrigation, Soil & Calendar
# ---------------------------------------------------------------------------
class IrrigationBase(BaseModel):
    date: str = Field(..., description="Date YYYY-MM-DD")
    block_name: str = Field("Block A", description="Farm block / zone")
    duration_or_quantity: Optional[str] = Field(None, description="Farmer entered quantity e.g. 2 hours or 1000L")
    notes: Optional[str] = Field(None, description="Optional notes")
    status: str = Field("COMPLETED", description="PENDING or COMPLETED")
    frequency_days: int = Field(7, description="Farmer configured recurrence frequency")

class IrrigationCreate(IrrigationBase):
    farm_id: int

class IrrigationResponse(IrrigationBase):
    id: int
    farm_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SoilTestBase(BaseModel):
    date: str = Field(..., description="Date YYYY-MM-DD")
    ph: float = Field(6.5, description="Soil pH value")
    nitrogen: float = Field(180.0, description="Nitrogen kg/ha")
    phosphorus: float = Field(18.0, description="Phosphorus kg/ha")
    potassium: float = Field(220.0, description="Potassium kg/ha")
    organic_carbon: float = Field(0.75, description="Organic carbon percentage")
    notes: Optional[str] = Field(None, description="Notes")

class SoilTestCreate(SoilTestBase):
    farm_id: int

class SoilTestResponse(SoilTestBase):
    id: int
    farm_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FarmActivityBase(BaseModel):
    activity_type: str = Field("fertilizer", description="fertilizer, irrigation, soil, pest, weed, general")
    title: str = Field(..., description="Activity title")
    age_bracket: Optional[str] = Field(None, description="0-3 years, 3-6 years, 6+ years")
    scheduled_date: str = Field(..., description="YYYY-MM-DD")
    status: str = Field("PENDING", description="PENDING or COMPLETED")
    completed_at: Optional[str] = Field(None, description="Completion date")
    notes: Optional[str] = Field(None, description="Notes")

class FarmActivityCreate(FarmActivityBase):
    farm_id: int

class FarmActivityResponse(FarmActivityBase):
    id: int
    farm_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------------------------------------------------------------------------
# Phase 3 Schemas — Expenses, Blocks & Growth Tracking
# ---------------------------------------------------------------------------
class ExpenseBase(BaseModel):
    category: str = Field(..., description="Expense category")
    amount: float = Field(..., gt=0, description="Expense amount")
    date: str = Field(..., description="YYYY-MM-DD")
    notes: Optional[str] = Field(None, description="Notes")

class ExpenseCreate(ExpenseBase):
    farm_id: int

class ExpenseResponse(ExpenseBase):
    id: int
    farm_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ExpenseSummaryResponse(BaseModel):
    total_investment: float
    monthly_expense: float
    category_breakdown: Dict[str, float]
    expense_count: int

class FarmBlockBase(BaseModel):
    block_name: str = Field(..., description="Block / Plot Name")
    tree_count: int = Field(0, ge=0, description="Tree count")
    planting_date: Optional[str] = Field(None, description="Planting date YYYY-MM-DD")
    variety: Optional[str] = Field("Hybrid (DxT)", description="Palm variety")
    status: str = Field("Active", description="Active, Nursery, Re-planting")
    notes: Optional[str] = Field(None, description="Notes")

class FarmBlockCreate(FarmBlockBase):
    farm_id: int

class FarmBlockResponse(FarmBlockBase):
    id: int
    farm_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class GrowthRecordBase(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    observation_notes: str = Field(..., description="Field observations")
    tree_height_m: Optional[float] = Field(None, description="Tree height meters")
    yield_nuts_per_tree: Optional[float] = Field(None, description="Nuts count per tree")
    photo_path: Optional[str] = Field(None, description="Photo path")

class GrowthRecordCreate(GrowthRecordBase):
    block_id: int

class GrowthRecordResponse(GrowthRecordBase):
    id: int
    block_id: int
    created_at: datetime

    class Config:
        from_attributes = True



