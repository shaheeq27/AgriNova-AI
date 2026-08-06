"""
AgriNova AI — Report response schemas.

Pydantic models for structured farm operation reports.
"""

from datetime import datetime
from pydantic import BaseModel


class ReportMeta(BaseModel):
    """Common metadata for all reports."""

    report_type: str
    generated_at: datetime
    period_start: str | None = None
    period_end: str | None = None


class TimelineSummary(BaseModel):
    """Summary of a crop's timeline stages."""

    total_stages: int
    completed_stages: int
    active_stage: str | None = None
    progress_percent: float


class TasksSummary(BaseModel):
    """Summary of task completion."""

    total: int
    completed: int
    overdue: int
    completion_percent: float


class CropReportData(BaseModel):
    """Data payload for a single-crop report."""

    crop_id: str
    crop_name: str
    farm_name: str
    status: str
    season: str
    planting_date: str | None = None
    expected_harvest_date: str | None = None
    area_acres: float
    timeline: TimelineSummary
    tasks: TasksSummary
    disease_count: int
    fertilizer_applications: int
    irrigation_applications: int


class CropReportResponse(BaseModel):
    """Full crop report."""

    meta: ReportMeta
    data: CropReportData


class FarmCropSummary(BaseModel):
    """Brief crop summary within a farm report."""

    crop_id: str
    crop_name: str
    status: str
    health_score: float


class FarmReportData(BaseModel):
    """Data payload for a farm report."""

    farm_id: str
    farm_name: str
    location: str
    total_area_acres: float
    soil_type: str
    total_crops: int
    active_crops: int
    harvested_crops: int
    crop_summaries: list[FarmCropSummary]
    total_tasks: int
    completed_tasks: int
    total_disease_records: int
    total_activities: int


class FarmReportResponse(BaseModel):
    """Full farm report."""

    meta: ReportMeta
    data: FarmReportData


class WeatherDayEntry(BaseModel):
    """Single day's weather in a report."""

    date: str
    temp_avg: float | None = None
    humidity: float | None = None
    rainfall: float | None = None
    condition: str | None = None


class WeatherReportData(BaseModel):
    """Data payload for a weather report."""

    farm_id: str
    farm_name: str
    entries: list[WeatherDayEntry]
    avg_temperature: float | None = None
    total_rainfall: float | None = None
    alert_count: int


class WeatherReportResponse(BaseModel):
    """Full weather report."""

    meta: ReportMeta
    data: WeatherReportData


class FertilizerEntry(BaseModel):
    """Single fertilizer application entry."""

    date: str
    fertilizer_type: str
    quantity: float | None = None
    growth_stage: str | None = None


class FertilizerReportData(BaseModel):
    """Data payload for a fertilizer report."""

    crop_id: str
    crop_name: str
    entries: list[FertilizerEntry]
    total_applications: int


class FertilizerReportResponse(BaseModel):
    """Full fertilizer report."""

    meta: ReportMeta
    data: FertilizerReportData


class IrrigationEntry(BaseModel):
    """Single irrigation log entry."""

    date: str
    water_amount_liters: float | None = None
    duration_minutes: float | None = None
    method: str | None = None


class IrrigationReportData(BaseModel):
    """Data payload for an irrigation report."""

    crop_id: str
    crop_name: str
    entries: list[IrrigationEntry]
    total_applications: int
    total_water_liters: float


class IrrigationReportResponse(BaseModel):
    """Full irrigation report."""

    meta: ReportMeta
    data: IrrigationReportData
