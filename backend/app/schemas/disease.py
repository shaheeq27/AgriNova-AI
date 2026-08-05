"""
AgriNova AI — Disease detection schemas.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class DiseaseDetectionRequest(BaseModel):
    """Schema for detecting a disease from symptoms."""

    crop_name: str = Field(..., min_length=2, max_length=100)
    symptoms: list[str] = Field(..., min_length=1)


class DiseaseMatch(BaseModel):
    """Schema for a matched disease based on symptoms."""

    disease_name: str
    confidence: float
    symptoms: list[str]
    treatment: str
    prevention: str
    severity: str
    explanation: str


class DiseaseDetectionResponse(BaseModel):
    """Response schema for disease detection."""

    matches: list[DiseaseMatch]
    model_version: str = "v1.0-symptom"


class DiseaseRecordCreate(BaseModel):
    """Schema for creating a disease record."""

    crop_id: str
    disease_name: str = Field(..., min_length=2, max_length=200)
    symptoms_observed: str | None = None
    severity: str = "medium"
    detection_source: str = "manual"
    notes: str | None = None


class DiseaseRecordUpdate(BaseModel):
    """Schema for updating a disease record."""

    status: str | None = Field(None, description="active | treated | resolved")
    treatment_applied: str | None = None
    notes: str | None = None
    resolved_at: datetime | None = None


class DiseaseImageResponse(BaseModel):
    """Schema for disease image response."""

    id: str
    file_path: str
    file_name: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DiseaseRecordResponse(BaseModel):
    """Schema for a disease record in API responses."""

    id: str
    crop_id: str
    disease_name: str
    confidence: float | None = None
    detection_source: str
    symptoms_observed: str | None = None
    treatment_applied: str | None = None
    severity: str
    status: str
    notes: str | None = None
    detected_at: datetime
    resolved_at: datetime | None = None
    images: list[DiseaseImageResponse] = []

    model_config = {"from_attributes": True}
