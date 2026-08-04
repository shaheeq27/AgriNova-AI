"""
AgriNova AI — Fertilizer log model.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FertilizerLog(Base):
    """Farmer's fertilizer application log — captures real outcomes for future ML v2."""

    __tablename__ = "fertilizer_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    crop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    fertilizer_type: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="kg")
    application_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    growth_stage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(
        String(20), default="manual"
    )  # manual | recommended
    observed_effect: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    crop = relationship("Crop", back_populates="fertilizer_logs")
