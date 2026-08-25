from datetime import date
from pydantic import BaseModel, Field

class CropPerformanceInsight(BaseModel):
    crop_name: str
    variety: str | None = None
    seasons_observed: list[str] = Field(default_factory=list)
    crops_observed: int = 0
    harvested_count: int = 0
    average_yield: float | None = None
    yield_unit: str | None = None
    best_yield: float | None = None
    worst_yield: float | None = None
    disease_records: int = 0
    fertilizer_applications: int = 0
    irrigation_applications: int = 0
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

class SeasonalPerformanceInsight(BaseModel):
    season: str
    crops_observed: int = 0
    harvested_crops: int = 0
    average_yield: float | None = None
    yield_unit: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

class DiseasePatternInsight(BaseModel):
    disease_name: str
    affected_crop: str
    occurrence_count: int = 0
    resolved_count: int = 0
    active_count: int = 0
    common_severity: str | None = None
    treatment_observed: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

class InputUsageInsight(BaseModel):
    input_type: str
    crop_name: str
    application_count: int = 0
    total_quantity: float | None = None
    quantity_unit: str | None = None
    common_application_method: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

class YieldTrendInsight(BaseModel):
    crop_name: str
    yield_unit: str
    observations: int = 0
    average_yield: float | None = None
    highest_yield: float | None = None
    lowest_yield: float | None = None
    trend_direction: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

class HistoricalInsightsContext(BaseModel):
    crop_performance: list[CropPerformanceInsight] = Field(default_factory=list)
    seasonal_performance: list[SeasonalPerformanceInsight] = Field(default_factory=list)
    disease_patterns: list[DiseasePatternInsight] = Field(default_factory=list)
    input_usage: list[InputUsageInsight] = Field(default_factory=list)
    yield_trends: list[YieldTrendInsight] = Field(default_factory=list)


