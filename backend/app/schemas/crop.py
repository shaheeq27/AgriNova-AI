"""
AgriNova AI — Crop & Recommendation schemas.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# ── Recommendation ──

class CropRecommendationRequest(BaseModel):
    """Input conditions for crop recommendation."""
    temperature: float = Field(..., ge=-10, le=55, description="Current temperature in °C")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    rainfall: float = Field(..., ge=0, le=1000, description="Rainfall in mm")
    soil_type: str = Field(..., min_length=2, description="Soil type (Clay, Loamy, etc.)")
    n: float = Field(50, ge=0, description="Nitrogen content")
    p: float = Field(35, ge=0, description="Phosphorus content")
    k: float = Field(35, ge=0, description="Potassium content")
    ph: float = Field(6.5, ge=3.0, le=10.0, description="Soil pH")
    farm_id: str | None = Field(None, description="Farm ID for personalized historical adjustments")


class CropRecommendation(BaseModel):
    """A single crop recommendation with explanation."""
    crop_name: str
    confidence: float
    explanation: str
    model_version: str
    historically_adjusted: bool = False
    personalization_rationale: str | None = None


class CropRecommendationResponse(BaseModel):
    """Response containing top crop recommendations."""
    recommendations: list[CropRecommendation]
    input_conditions: dict


# ── Crop CRUD ──

class CropCreate(BaseModel):
    """Request to plant a crop on a farm."""
    farm_id: str
    crop_name: str = Field(..., min_length=2, max_length=100)
    variety: str | None = Field(None, max_length=100)
    season: str = Field(..., min_length=2, max_length=50)
    area_acres: float = Field(..., gt=0)
    planting_date: date | None = None
    notes: str | None = None
    recommendation_score: float | None = None
    recommendation_source: str | None = None
    yield_amount: float | None = None
    yield_unit: str | None = "kg"


class CropUpdate(BaseModel):
    """Partial update for a crop."""
    status: str | None = None
    variety: str | None = Field(None, max_length=100)
    planting_date: date | None = None
    expected_harvest_date: date | None = None
    actual_harvest_date: date | None = None
    area_acres: float | None = None
    notes: str | None = None
    yield_amount: float | None = None
    yield_unit: str | None = None


class CropResponse(BaseModel):
    """Full crop record response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    farm_id: str
    crop_name: str
    variety: str | None
    season: str
    planting_date: date | None
    expected_harvest_date: date | None
    actual_harvest_date: date | None
    area_acres: float
    status: str
    yield_amount: float | None
    yield_unit: str | None
    recommendation_score: float | None
    recommendation_source: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class CropListResponse(BaseModel):
    """List of crops."""
    crops: list[CropResponse]
    total: int


# ── Timeline ──

class TimelineStageResponse(BaseModel):
    """A single timeline stage for a crop."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    crop_id: str
    stage_name: str
    stage_order: int
    start_date: date
    end_date: date
    status: str


class TimelineResponse(BaseModel):
    """Full timeline for a crop."""
    stages: list[TimelineStageResponse]
    total_days: int
    current_stage: str | None


# ── Daily Tasks ──

class DailyTaskResponse(BaseModel):
    """A daily task for a crop."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None
    scheduled_date: date
    priority: str
    category: str
    is_completed: bool
    completed_at: datetime | None
    notes: str | None


class DailyTaskUpdate(BaseModel):
    """Update a daily task."""
    is_completed: bool | None = None
    notes: str | None = None


class TaskListResponse(BaseModel):
    """List of tasks with summary."""
    tasks: list[DailyTaskResponse]
    total: int
    completed_count: int
