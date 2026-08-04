"""
AgriNova AI — Weather record model.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WeatherRecord(Base):
    """Daily weather observation for a farm — from API or manual entry."""

    __tablename__ = "weather_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    farm_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    temp_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    temp_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    temp_avg: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall: Mapped[float] = mapped_column(Float, default=0.0)
    wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    condition: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="open-meteo")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    farm = relationship("Farm", back_populates="weather_records")
