"""
AgriNova AI — Crop Recommendation V6 Schemas.
"""

from typing import Any
from pydantic import BaseModel, Field

class ExplanationPayload(BaseModel):
    """Deterministic explanation payload for V6 engine."""
    base_explanation: str
    positive_factors: list[str] = Field(default_factory=list)
    negative_factors: list[str] = Field(default_factory=list)
    constraints_applied: list[str] = Field(default_factory=list)


class CropRecommendationV6(BaseModel):
    """A single crop recommendation for V6 engine."""
    crop_name: str
    final_score: float
    base_score: float
    explanation: ExplanationPayload
    personalization_applied: bool = False
    engine_version: str


class CropRecommendationRequestV6(BaseModel):
    """V6 Input conditions for crop recommendation."""
    farm_id: str | None = Field(None, description="Farm ID for personalized historical adjustments")
    soil_type: str = Field(..., min_length=2, description="Soil type (Clay, Loamy, etc.)")
    season: str | None = Field(None, description="Target growing season")
    temperature: float | None = Field(None, description="Current/Forecast temperature in °C")
    humidity: float | None = Field(None, description="Humidity percentage")
    rainfall: float | None = Field(None, description="Rainfall in mm")


class CropRecommendationResponseV6(BaseModel):
    """V6 Response containing top crop recommendations."""
    recommendations: list[CropRecommendationV6]
    input_conditions_used: dict[str, Any]
