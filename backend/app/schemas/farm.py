"""
AgriNova AI — Farm schemas.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class FarmCreate(BaseModel):
    """Schema for creating a new farm."""

    name: str = Field(..., min_length=2, max_length=255)
    location_city: str = Field(..., min_length=2, max_length=255)
    location_state: str | None = Field(None, max_length=255)
    total_area_acres: float = Field(..., gt=0)
    soil_type: str = Field(..., min_length=2, max_length=50)
    water_source: str | None = Field(None, max_length=100)
    description: str | None = None


class FarmUpdate(BaseModel):
    """Schema for updating a farm."""

    name: str | None = Field(None, min_length=2, max_length=255)
    location_city: str | None = Field(None, min_length=2, max_length=255)
    location_state: str | None = Field(None, max_length=255)
    total_area_acres: float | None = Field(None, gt=0)
    soil_type: str | None = Field(None, min_length=2, max_length=50)
    water_source: str | None = Field(None, max_length=100)
    description: str | None = None


class CropSummary(BaseModel):
    """Minimal crop info shown inside farm responses."""

    id: str
    crop_name: str
    status: str
    area_acres: float

    model_config = {"from_attributes": True}


class FarmResponse(BaseModel):
    """Schema for farm data in API responses."""

    id: str
    user_id: str
    name: str
    location_city: str
    location_state: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    total_area_acres: float
    soil_type: str
    water_source: str | None = None
    description: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    crops: list[CropSummary] = []

    model_config = {"from_attributes": True}


class FarmListResponse(BaseModel):
    """Schema for listing farms."""

    farms: list[FarmResponse]
    total: int

from app.ai.schemas.historical_analysis import (
    CropPerformanceInsight,
    SeasonalPerformanceInsight,
    DiseasePatternInsight,
    InputUsageInsight,
    YieldTrendInsight,
)

class FarmInsightsResponse(BaseModel):
    """Schema for returning historical farm insights to the frontend."""
    crop_performance: list[CropPerformanceInsight]
    seasonal_performance: list[SeasonalPerformanceInsight]
    disease_patterns: list[DiseasePatternInsight]
    input_usage: list[InputUsageInsight]
    yield_trends: list[YieldTrendInsight]
