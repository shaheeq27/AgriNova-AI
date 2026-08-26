"""
AgriNova AI — Context schemas for the AI Context Engine.

Phase 3: farm + weather context.
Phase 4: + knowledge (structured RAG from AgriNova KB).
Phase 6: + intelligence (engine outputs).
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field
from app.ai.schemas.historical_analysis import HistoricalInsightsContext


# ── Crop context ─────────────────────────────────────────────────────────────

class CropContext(BaseModel):
    """Context for a single crop planted on the farm."""

    crop_id: str | None = None  # Phase 6: needed for timeline lookup
    crop_name: str
    season: str
    planting_date: date | None = None
    expected_harvest_date: date | None = None
    status: str  # planned | active | harvested | abandoned
    area_acres: float


# ── Weather context ──────────────────────────────────────────────────────────

class WeatherContext(BaseModel):
    """Single day of weather data (historical or forecast)."""

    date: date
    temp_min: float | None = None
    temp_max: float | None = None
    temp_avg: float | None = None
    rainfall: float = 0.0
    humidity: float | None = None
    wind_speed: float | None = None
    condition: str | None = None


class WeatherData(BaseModel):
    """Combined historical + forecast weather for a farm."""

    historical: list[WeatherContext] = Field(default_factory=list)
    forecast: list[WeatherContext] = Field(default_factory=list)


# ── Farm context ─────────────────────────────────────────────────────────────

class FarmContext(BaseModel):
    """Structured context for the user's farm."""

    name: str
    location_city: str
    location_state: str | None = None
    soil_type: str
    total_area_acres: float
    water_source: str | None = None
    crops: list[CropContext] = Field(default_factory=list)


# ── Knowledge context (Structured RAG) ──────────────────────────────────────

class CropKnowledge(BaseModel):
    """Knowledge retrieved from the AgriNova KB for a single crop.

    Fields contain pre-formatted summaries assembled by
    ``KnowledgeService``, not raw ORM objects.
    """

    crop_name: str
    profile_description: str | None = None
    ideal_conditions: str | None = None
    growth_stages: list[str] = Field(default_factory=list)
    diseases: list[str] = Field(default_factory=list)
    fertilizer_schedule: list[str] = Field(default_factory=list)
    irrigation_guidelines: list[str] = Field(default_factory=list)


class RAGContext(BaseModel):
    """Knowledge retrieved from the AgriNova knowledge base.

    Phase 4: structured retrieval scoped to the farmer's actual crops.
    """

    crop_knowledge: list[CropKnowledge] = Field(default_factory=list)


# ── Intelligence context (Engine outputs) ───────────────────────────────────

class IrrigationResult(BaseModel):
    """Structured irrigation engine output for a single crop."""

    water_requirement_mm: float
    frequency: str
    method: str
    explanation: str
    weather_adjusted: bool = False
    historically_adjusted: bool = False
    personalization_rationale: str | None = None


class FertilizerResult(BaseModel):
    """Structured fertilizer engine output for a single crop."""

    fertilizer_type: str
    quantity_per_acre: float
    unit: str
    timing: str
    application_method: str
    explanation: str
    historically_adjusted: bool = False
    personalization_rationale: str | None = None


class DiseaseResult(BaseModel):
    """Structured disease detection output."""

    disease_name: str
    confidence: float
    symptoms: list[str] = Field(default_factory=list)
    treatment: str | None = None
    prevention: str | None = None
    severity: str | None = None
    explanation: str | None = None
    historically_adjusted: bool = False
    personalization_rationale: str | None = None


class CropEngineOutput(BaseModel):
    """Engine outputs for a single crop."""

    crop_name: str
    current_stage: str | None = None
    irrigation: IrrigationResult | None = None
    fertilizer: FertilizerResult | None = None
    diseases: list[DiseaseResult] = Field(default_factory=list)


class EngineContext(BaseModel):
    """Intelligence engine outputs for the farmer's crops.

    Phase 6: populated by ``IntelligenceService`` based on
    intent-aware engine selection.
    """

    crop_outputs: list[CropEngineOutput] = Field(default_factory=list)


# ── History context ──────────────────────────────────────────────────────────

class CropHistoryEntry(BaseModel):
    crop_name: str
    variety: str | None = None
    season: str
    planting_date: date | None = None
    harvest_date: date | None = None
    yield_amount: float | None = None
    yield_unit: str | None = None
    status: str
    disease_count: int = 0
    fertilizer_applications: int = 0
    irrigation_applications: int = 0


class FarmHistoryContext(BaseModel):
    past_crops: list[CropHistoryEntry] = Field(default_factory=list)
    recent_diseases: list[str] = Field(default_factory=list)
    seasonal_patterns: list[str] = Field(default_factory=list)
    performance_summary: str | None = None


class HistoricalInsights(BaseModel):
    """Deterministic insights extracted from farm history."""
    successful_crops: list[str] = Field(default_factory=list)
    recurring_diseases: list[str] = Field(default_factory=list)
    seasonal_crop_patterns: list[str] = Field(default_factory=list)
    historical_yield_observations: list[str] = Field(default_factory=list)


# ── Unified Context ─────────────────────────────────────────────────────────

class UnifiedContext(BaseModel):
    """Top-level context container passed to the ContextFormatter.

    Phase 3: ``farm`` + ``weather`` are populated.
    Phase 4: ``knowledge`` is populated (structured RAG).
    Phase 6: ``intelligence`` is populated (engine outputs).
    Phase 8 (V4 Phase 1): ``history`` is populated.
    Phase 9 (V4 Phase 1): ``historical_insights`` is populated.
    """

    farm: FarmContext | None = None
    weather: WeatherData | None = None
    knowledge: RAGContext | None = None
    intelligence: EngineContext | None = None
    history: FarmHistoryContext | None = None
    historical_insights: HistoricalInsightsContext | None = None
