"""
AgriNova AI — Timeline & Daily Task models.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CropTimeline(Base):
    """An instantiated timeline for a planted crop — generated from KB templates."""

    __tablename__ = "crop_timelines"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    crop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage_name: Mapped[str] = mapped_column(String(100), nullable=False)
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="upcoming"
    )  # upcoming | active | completed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    crop = relationship("Crop", back_populates="timeline")
    tasks = relationship("DailyTask", back_populates="timeline_stage", lazy="selectin")


class DailyTask(Base):
    """Individual task derived from a timeline stage — the farmer's to-do item."""

    __tablename__ = "daily_tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    timeline_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("crop_timelines.id", ondelete="CASCADE"), nullable=False, index=True
    )
    crop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    category: Mapped[str] = mapped_column(String(50), default="general")
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    timeline_stage = relationship("CropTimeline", back_populates="tasks")
