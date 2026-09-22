"""
AgriNova AI — Knowledge Base schemas.
"""

from pydantic import BaseModel


class CropProfileResponse(BaseModel):
    """Schema for crop profile data."""

    id: str
    crop_name: str
    description: str | None = None
    temp_min: float
    temp_max: float
    rain_min: float
    rain_max: float
    humidity_min: float
    humidity_max: float
    ideal_soil_types: str
    ideal_ph_min: float | None = None
    ideal_ph_max: float | None = None
    growing_season: str
    botanical_family: str | None = None
    water_requirement_mm: float | None = None
    total_duration_days: int | None = None
    image_url: str | None = None

    model_config = {"from_attributes": True}


class GrowthStageResponse(BaseModel):
    """Schema for growth stage data."""

    id: str
    crop_name: str
    stage_name: str
    stage_order: int
    duration_days: int
    description: str | None = None
    key_activities: str | None = None

    model_config = {"from_attributes": True}


class DiseaseLibraryResponse(BaseModel):
    """Schema for disease library entry."""

    id: str
    disease_name: str
    affected_crops: str
    symptoms: str
    treatment: str
    prevention: str
    severity: str
    image_url: str | None = None

    model_config = {"from_attributes": True}


class FertilizerLibraryResponse(BaseModel):
    """Schema for fertilizer guideline entry."""

    id: str
    crop_name: str
    stage_name: str
    fertilizer_type: str
    quantity_per_acre: float
    unit: str
    timing: str
    application_method: str | None = None
    notes: str | None = None

    model_config = {"from_attributes": True}


class IrrigationGuidelineResponse(BaseModel):
    """Schema for irrigation guideline entry."""

    id: str
    crop_name: str
    stage_name: str
    soil_type: str
    water_requirement_mm: float
    frequency: str
    method: str | None = None
    notes: str | None = None

    model_config = {"from_attributes": True}
