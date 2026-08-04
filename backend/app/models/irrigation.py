"""
AgriNova AI — Irrigation log model.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class IrrigationLog(Base):
    """Farmer's irrigation activity log — captures real inputs for future ML."""

    __tablename__ = "irrigation_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    crop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    water_amount_liters: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)
    method: Mapped[str | None] = mapped_column(String(100), nullable=True)  # drip | sprinkler | flood | manual
    source: Mapped[str] = mapped_column(
        String(20), default="manual"
    )  # manual | recommended | sensor
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    crop = relationship("Crop", back_populates="irrigation_logs")
