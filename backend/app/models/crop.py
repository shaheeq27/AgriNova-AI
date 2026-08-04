"""
AgriNova AI — Crop model.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Crop(Base):
    """A crop planted (or planned) on a specific farm."""

    __tablename__ = "crops"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    farm_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    season: Mapped[str] = mapped_column(String(50), nullable=False)
    planting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expected_harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    area_acres: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="planned"
    )  # planned | active | harvested | abandoned
    recommendation_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    recommendation_source: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # ml | rule | manual
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    farm = relationship("Farm", back_populates="crops")
    timeline = relationship("CropTimeline", back_populates="crop", lazy="selectin")
    disease_records = relationship("DiseaseRecord", back_populates="crop", lazy="select")
    irrigation_logs = relationship("IrrigationLog", back_populates="crop", lazy="select")
    fertilizer_logs = relationship("FertilizerLog", back_populates="crop", lazy="select")
