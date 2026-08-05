"""
AgriNova AI — Fertilizer schemas.
"""

from datetime import date
from pydantic import BaseModel


class FertilizerRecommendation(BaseModel):
    fertilizer_type: str
    quantity_per_acre: float
    unit: str
    timing: str
    application_method: str | None
    explanation: str


class FertilizerLogCreate(BaseModel):
    crop_id: str
    date: date
    fertilizer_type: str
    quantity: float
    unit: str = "kg"
    application_method: str | None = None
    growth_stage: str | None = None
    notes: str | None = None


class FertilizerLogResponse(BaseModel):
    id: str
    crop_id: str
    date: date
    fertilizer_type: str
    quantity: float
    unit: str
    application_method: str | None
    growth_stage: str | None
    source: str
    observed_effect: str | None
    notes: str | None

    model_config = {"from_attributes": True}
