"""
AgriNova AI — V6 Recommendation Context.
"""

from typing import Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.farm import Farm
from app.models.crop import Crop
from app.models.weather import WeatherRecord
from app.ai.schemas.historical_analysis import (
    HistoricalInsightsContext,
    DiseasePatternInsight,
    YieldTrendInsight,
    CropPerformanceInsight
)

class RecommendationContext(BaseModel):
    """
    Strongly typed context for V6 crop recommendation.
    Distinguishes clearly between available and missing historical information.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Required inputs
    soil_type: str
    
    # Inputs that can be provided directly or inferred from farm
    location: dict[str, float] | None = None  # e.g., {"latitude": 0.0, "longitude": 0.0}
    season: str | None = None
    water_source: str | None = None
    
    # Weather
    temperature: float | None = None
    humidity: float | None = None
    rainfall: float | None = None
    current_weather: WeatherRecord | None = None
    weather_history: list[WeatherRecord] | None = None
    
    # Optional Farm context
    farm: Any | None = None  # Using Any to avoid strict pydantic validation of SQLAlchemy models if needed, or Farm
    farm_id: str | None = None
    
    # Farm History
    previous_crop: str | None = None
    previous_crop_family: str | None = None
    
    # Processed historical insights
    disease_history: list[DiseasePatternInsight] | None = None
    farm_performance: HistoricalInsightsContext | None = None
