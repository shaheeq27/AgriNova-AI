"""
AgriNova AI — Crop Recommendation V6 Schemas.
"""

from typing import Any
from pydantic import BaseModel, Field

from app.schemas.crop_v6_domain import AgronomicSuitability, BiologicalRisk, HistoricalEvidence, HardConstraint

class ExplanationPayload(BaseModel):
    """Deterministic explanation payload for V6 engine."""
    base_explanation: str
    positive_factors: list[str] = Field(default_factory=list)
    negative_factors: list[str] = Field(default_factory=list)
    constraints_applied: list[str] = Field(default_factory=list)
    evidence_coverage_ratio: float = Field(1.0, ge=0.0, le=1.0)


class CropRecommendationV6(BaseModel):
    """A single crop recommendation for V6 engine."""
    crop_name: str
    final_score: float
    base_score: float
    explanation: ExplanationPayload
    personalization_applied: bool = False
    engine_version: str
    agronomic_suitability: AgronomicSuitability | None = None
    eligibility_constraints: list[HardConstraint] = Field(default_factory=list)
    biological_risks: list[BiologicalRisk] = Field(default_factory=list)
    historical_evidence: HistoricalEvidence | None = None


class CropRecommendationRequestV6(BaseModel):
    """V6 Input conditions for crop recommendation."""
    farm_id: str | None = Field(None, description="Farm ID for personalized historical adjustments")
    location_name: str | None = Field(None, description="Arbitrary typed location for weather resolution")
    water_source: str | None = Field(None, description="Irrigation water source")
    soil_type: str = Field(..., min_length=2, description="Soil type (Clay, Loamy, etc.)")
    season: str | None = Field(None, description="Target growing season")
    temperature: float | None = Field(None, description="Current/Forecast temperature in °C")
    humidity: float | None = Field(None, description="Humidity percentage")
    rainfall: float | None = Field(None, description="Rainfall in mm")


class CropRecommendationResponseV6(BaseModel):
    """V6 Response containing top crop recommendations."""
    recommendations: list[CropRecommendationV6]
    input_conditions_used: dict[str, Any]
