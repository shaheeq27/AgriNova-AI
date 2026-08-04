"""
AgriNova AI — Knowledge Base models.

The shared backbone powering Timeline, Disease, Fertilizer, and Irrigation modules.
These tables hold reference/agronomic data — not user-generated content.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CropProfile(Base):
    """Reference profile for a crop — ideal growing conditions."""

    __tablename__ = "kb_crop_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    crop_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    temp_min: Mapped[float] = mapped_column(Float, nullable=False)
    temp_max: Mapped[float] = mapped_column(Float, nullable=False)
    rain_min: Mapped[float] = mapped_column(Float, nullable=False)
    rain_max: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_min: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_max: Mapped[float] = mapped_column(Float, nullable=False)
    ideal_soil_types: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # comma-separated list
    ideal_ph_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    ideal_ph_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    growing_season: Mapped[str] = mapped_column(String(50), nullable=False)
    total_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class GrowthStage(Base):
    """Growth stages for a crop (e.g., Germination → Vegetative → Flowering → Harvest)."""

    __tablename__ = "kb_growth_stages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stage_name: Mapped[str] = mapped_column(String(100), nullable=False)
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_activities: Mapped[str | None] = mapped_column(Text, nullable=True)


class TimelineTemplate(Base):
    """Template tasks for each crop and growth stage — used to generate CropTimeline entries."""

    __tablename__ = "kb_timeline_templates"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stage_name: Mapped[str] = mapped_column(String(100), nullable=False)
    day_offset_start: Mapped[int] = mapped_column(Integer, nullable=False)
    day_offset_end: Mapped[int] = mapped_column(Integer, nullable=False)
    task_title: Mapped[str] = mapped_column(String(255), nullable=False)
    task_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low | medium | high | critical
    category: Mapped[str] = mapped_column(String(50), default="general")  # irrigation | fertilizer | pest_control | general


class DiseaseLibrary(Base):
    """Reference data for crop diseases — symptoms, treatment, prevention."""

    __tablename__ = "kb_disease_library"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    disease_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    affected_crops: Mapped[str] = mapped_column(Text, nullable=False)  # comma-separated
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)
    treatment: Mapped[str] = mapped_column(Text, nullable=False)
    prevention: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium")  # low | medium | high | critical
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class FertilizerLibrary(Base):
    """Fertilizer guidelines per crop and growth stage."""

    __tablename__ = "kb_fertilizer_library"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stage_name: Mapped[str] = mapped_column(String(100), nullable=False)
    fertilizer_type: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity_per_acre: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="kg")
    timing: Mapped[str] = mapped_column(String(255), nullable=False)
    application_method: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class IrrigationGuideline(Base):
    """Water requirement guidelines per crop, stage, and soil type."""

    __tablename__ = "kb_irrigation_guidelines"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stage_name: Mapped[str] = mapped_column(String(100), nullable=False)
    soil_type: Mapped[str] = mapped_column(String(50), nullable=False)
    water_requirement_mm: Mapped[float] = mapped_column(Float, nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)
    method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
