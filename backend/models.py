from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    preferred_language = Column(String(5), nullable=False, default="en")


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_image_path = Column(String(500), nullable=False)
    annotated_image_path = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(50), nullable=False, default="Healthy") # Healthy, Diseased, Warning
    total_detections = Column(Integer, default=0)
    primary_disease = Column(String(100), default="Healthy")
    max_confidence = Column(Float, default=0.0)
    confidence_threshold = Column(Float, default=0.5)
    block_id = Column(Integer, ForeignKey("farm_blocks.id", ondelete="SET NULL"), nullable=True)
    farmer_notes = Column(Text, nullable=True)

    results = relationship("DetectionResult", back_populates="detection", cascade="all, delete-orphan")
    block = relationship("FarmBlock", backref="detections")


class DetectionResult(Base):
    __tablename__ = "detection_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    detection_id = Column(Integer, ForeignKey("detections.id", ondelete="CASCADE"), nullable=False)
    class_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    severity = Column(String(50), default="Low")

    detection = relationship("Detection", back_populates="results")


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(150), nullable=False)
    land_area = Column(Float, nullable=False, default=1.0)
    land_unit = Column(String(20), nullable=False, default="acres") # acres or hectares
    soil_type = Column(String(50), nullable=False, default="loamy") # sandy, loamy, clayey, red, laterite
    water_source = Column(String(100), nullable=True, default="Borewell")
    irrigation_method = Column(String(100), nullable=True, default="Drip")
    existing_trees = Column(Integer, nullable=False, default=0)
    planting_date = Column(String(50), nullable=True) # YYYY-MM-DD or string
    soil_test_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="farm", uselist=False)


class IrrigationRecord(Base):
    __tablename__ = "irrigation_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(String(50), nullable=False) # YYYY-MM-DD
    block_name = Column(String(100), nullable=False, default="Block A")
    duration_or_quantity = Column(String(100), nullable=True) # Farmer-entered only
    notes = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="COMPLETED") # PENDING / COMPLETED
    frequency_days = Column(Integer, nullable=False, default=7) # Farmer configured frequency
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", backref="irrigation_records")


class SoilTest(Base):
    __tablename__ = "soil_tests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(String(50), nullable=False) # YYYY-MM-DD
    ph = Column(Float, nullable=False, default=6.5)
    nitrogen = Column(Float, nullable=False, default=180.0) # kg/ha
    phosphorus = Column(Float, nullable=False, default=18.0) # kg/ha
    potassium = Column(Float, nullable=False, default=220.0) # kg/ha
    organic_carbon = Column(Float, nullable=False, default=0.75) # %
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", backref="soil_tests")


class FarmActivity(Base):
    __tablename__ = "farm_activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False, default="fertilizer") # fertilizer, irrigation, soil, pest, weed, general
    title = Column(String(200), nullable=False)
    age_bracket = Column(String(50), nullable=True) # 0-3 years, 3-6 years, 6+ years
    scheduled_date = Column(String(50), nullable=False) # YYYY-MM-DD
    status = Column(String(50), nullable=False, default="PENDING") # PENDING / COMPLETED
    completed_at = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", backref="activities")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    date = Column(String(50), nullable=False) # YYYY-MM-DD
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", backref="expenses")


class FarmBlock(Base):
    __tablename__ = "farm_blocks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    block_name = Column(String(100), nullable=False)
    tree_count = Column(Integer, nullable=False, default=0)
    planting_date = Column(String(50), nullable=True) # YYYY-MM-DD
    variety = Column(String(100), nullable=True, default="Hybrid (DxT)")
    status = Column(String(50), nullable=False, default="Active") # Active, Nursery, Re-planting
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", backref="blocks")
    growth_records = relationship("GrowthRecord", back_populates="block", cascade="all, delete-orphan")


class GrowthRecord(Base):
    __tablename__ = "growth_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    block_id = Column(Integer, ForeignKey("farm_blocks.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(String(50), nullable=False) # YYYY-MM-DD
    observation_notes = Column(Text, nullable=False)
    tree_height_m = Column(Float, nullable=True)
    yield_nuts_per_tree = Column(Float, nullable=True)
    photo_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    block = relationship("FarmBlock", back_populates="growth_records")



