"""
AgriNova AI — Irrigation schemas.
"""

from datetime import date
from pydantic import BaseModel


class IrrigationRecommendation(BaseModel):
    water_requirement_mm: float
    frequency: str
    method: str | None
    explanation: str
    weather_adjusted: bool


class IrrigationLogCreate(BaseModel):
    crop_id: str
    date: date
    water_amount_liters: float | None = None
    duration_minutes: float | None = None
    method: str | None = None
    growth_stage: str | None = None
    notes: str | None = None


class IrrigationLogResponse(BaseModel):
    id: str
    crop_id: str
    date: date
    water_amount_liters: float | None
    duration_minutes: float | None
    method: str | None
    growth_stage: str | None
    source: str
    notes: str | None

    model_config = {"from_attributes": True}
