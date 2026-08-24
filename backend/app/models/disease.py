"""
AgriNova AI — Disease detection models.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DiseaseRecord(Base):
    """A disease detection event for a crop — from CV model or manual entry."""

    __tablename__ = "disease_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    crop_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False, index=True
    )
    disease_name: Mapped[str] = mapped_column(String(200), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    detection_source: Mapped[str] = mapped_column(
        String(20), default="manual"
    )  # cv_model | manual
    symptoms_observed: Mapped[str | None] = mapped_column(Text, nullable=True)
    treatment_applied: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(
        String(20), default="active"
    )  # active | treated | resolved
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    crop = relationship("Crop", back_populates="disease_records")
    images = relationship("DiseaseImage", back_populates="record", lazy="selectin")


class DiseaseImage(Base):
    """Uploaded image linked to a disease detection record."""

    __tablename__ = "disease_images"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    record_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("disease_records.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    record = relationship("DiseaseRecord", back_populates="images")
