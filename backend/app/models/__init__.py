"""
AgriNova AI — Models package.

Imports all models so SQLAlchemy Base.metadata sees them for table creation.
"""

from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.knowledge import (
    CropProfile,
    GrowthStage,
    TimelineTemplate,
    DiseaseLibrary,
    FertilizerLibrary,
    IrrigationGuideline,
)
from app.models.weather import WeatherRecord
from app.models.timeline import CropTimeline, DailyTask
from app.models.disease import DiseaseRecord, DiseaseImage
from app.models.irrigation import IrrigationLog
from app.models.fertilizer import FertilizerLog

__all__ = [
    "User",
    "Farm",
    "Crop",
    "CropProfile",
    "GrowthStage",
    "TimelineTemplate",
    "DiseaseLibrary",
    "FertilizerLibrary",
    "IrrigationGuideline",
    "WeatherRecord",
    "CropTimeline",
    "DailyTask",
    "DiseaseRecord",
    "DiseaseImage",
    "IrrigationLog",
    "FertilizerLog",
]
