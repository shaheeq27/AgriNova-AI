"""
AgriNova AI — Disease service.

Business logic for disease detection and record management.
"""

import os
import uuid
from datetime import datetime, timezone

import aiofiles
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.schemas.historical_analysis import HistoricalInsightsContext

from app.core.exceptions import NotFoundException, AgriNovaException
from app.models.disease import DiseaseImage, DiseaseRecord
from app.models.knowledge import DiseaseLibrary
from app.repositories.disease_repo import DiseaseRepository
from app.schemas.disease import (
    DiseaseMatch,
    DiseaseRecordCreate,
    DiseaseRecordResponse,
    DiseaseRecordUpdate,
)
from app.services.activity_service import ActivityService


class DiseaseService:
    """Disease detection business logic."""

    def __init__(self, db: AsyncSession):
        self.repo = DiseaseRepository(db)
        self.db = db

    def _jaccard_similarity(self, list1: list[str], list2: list[str]) -> float:
        """Calculate Jaccard similarity between two lists of strings."""
        set1 = set([item.lower().strip() for item in list1])
        set2 = set([item.lower().strip() for item in list2])
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        if not union:
            return 0.0
        return len(intersection) / len(union)

    async def detect_from_symptoms(
        self, crop_name: str, symptoms: list[str],
        historical_insights: HistoricalInsightsContext | None = None
    ) -> list[DiseaseMatch]:
        """Detect diseases based on symptoms matching with the Knowledge Base."""
        # Fetch diseases for this crop
        result = await self.db.execute(
            select(DiseaseLibrary).where(DiseaseLibrary.affected_crops.ilike(f"%{crop_name}%"))
        )
        diseases = result.scalars().all()

        matches = []
        for disease in diseases:
            # Tokenize KB symptoms
            kb_symptoms = [s.strip() for s in disease.symptoms.split(",")]
            
            # Calculate confidence score
            confidence = self._jaccard_similarity(symptoms, kb_symptoms)
            
            if confidence > 0.1:  # Threshold for matching
                matches.append(
                    DiseaseMatch(
                        disease_name=disease.disease_name,
                        confidence=confidence,
                        symptoms=kb_symptoms,
                        treatment=disease.treatment,
                        prevention=disease.prevention,
                        severity=disease.severity,
                        explanation=f"Based on symptoms {symptoms}, this matches {disease.disease_name} which affects {crop_name}. Confidence: {int(confidence * 100)}%"
                    )
                )

        # V4 Phase 3: Deterministic Historical Personalization
        if historical_insights and historical_insights.disease_patterns:
            for match in matches:
                for pattern in historical_insights.disease_patterns:
                    if pattern.disease_name.lower() == match.disease_name.lower() and pattern.affected_crop.lower() == crop_name.lower():
                        if pattern.confidence is None or pattern.confidence < 0.6:
                            continue
                        if pattern.occurrence_count >= 1:
                            # Max 5% boost for historical recurrence, bounded
                            boost = min(0.05, pattern.occurrence_count * 0.025)
                            match.confidence = min(1.0, match.confidence + boost)
                            match.historically_adjusted = True
                            match.personalization_rationale = f"Confidence increased by {int(boost*100)}% due to historical recurrence of this disease on this crop (confidence: {pattern.confidence:.2f})."
                        break

        # Sort matches by confidence descending
        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches[:3]  # Return top 3 matches

    async def upload_image(self, crop_id: str, file: UploadFile) -> DiseaseImage:
        """Upload an image for a crop's disease record."""
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise AgriNovaException("Invalid file type. Allowed types: jpeg, png, webp.", status_code=400)

        # Create directory if it doesn't exist
        upload_dir = f"/Users/shaheeq.s/AgriNova-AI/backend/uploads/disease_images/{crop_id}"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Save file asynchronously
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            # Max size 10MB check
            if len(content) > 10 * 1024 * 1024:
                raise AgriNovaException("File too large. Maximum size is 10MB.", status_code=400)
            await out_file.write(content)

        # Create DiseaseImage record (will be linked to a record later or dummy for V1)
        image = DiseaseImage(
            record_id="temp",  # This should be updated when the record is created
            file_path=file_path,
            file_name=file.filename or unique_filename,
            content_type=file.content_type,
        )
        # Note: In a real flow we'd likely link it to the record properly.
        # But per requirements we return a DiseaseImage model to be saved.
        return image

    async def create_record(self, crop_id: str, data: DiseaseRecordCreate) -> DiseaseRecordResponse:
        """Create a new disease record."""
        record = DiseaseRecord(
            crop_id=crop_id,
            disease_name=data.disease_name,
            symptoms_observed=data.symptoms_observed,
            severity=data.severity,
            detection_source=data.detection_source,
            notes=data.notes,
        )
        record = await self.repo.create_record(record)
        return DiseaseRecordResponse.model_validate(record)

    async def create_record_with_logging(
        self, user_id: str, crop_id: str, data: DiseaseRecordCreate
    ) -> DiseaseRecordResponse:
        """Create a new disease record with activity logging."""
        result = await self.create_record(crop_id, data)

        activity = ActivityService(self.db)
        await activity.log_activity(
            user_id=user_id,
            action="disease_detected",
            entity_type="disease",
            entity_id=result.id,
            description=f"Detected disease '{data.disease_name}'",
            crop_id=crop_id,
        )

        return result

    async def get_records(self, crop_id: str) -> list[DiseaseRecordResponse]:
        """Get all disease records for a crop."""
        records = await self.repo.get_by_crop_id(crop_id)
        return [DiseaseRecordResponse.model_validate(r) for r in records]

    async def update_record(self, user_id: str, record_id: str, data: DiseaseRecordUpdate) -> DiseaseRecordResponse:
        """Update a disease record."""
        record = await self.repo.get_by_id(record_id)
        if not record:
            raise NotFoundException("DiseaseRecord", record_id)

        from app.models.crop import Crop
        import json
        
        crop_result = await self.db.execute(select(Crop).where(Crop.id == record.crop_id))
        crop = crop_result.scalar_one_or_none()

        old_status = record.status
        old_treatment = record.treatment_applied

        update_data = data.model_dump(exclude_unset=True)
        if "status" in update_data and update_data["status"] == "resolved" and not record.resolved_at:
            update_data["resolved_at"] = datetime.now(timezone.utc)
            
        record = await self.repo.update_record(record, **update_data)

        activity = ActivityService(self.db)
        metadata = {
            "disease_name": record.disease_name,
            "severity": record.severity,
            "treatment_applied": record.treatment_applied,
            "outcome": record.outcome,
            "status": record.status,
            "detected_at": record.detected_at.isoformat() if record.detected_at else None,
            "resolved_at": record.resolved_at.isoformat() if record.resolved_at else None
        }

        # Log treatment if changed
        if "treatment_applied" in update_data and update_data["treatment_applied"] != old_treatment:
            await activity.log_activity(
                user_id=user_id,
                action="disease_treated",
                entity_type="disease",
                entity_id=record.id,
                description=f"Applied treatment for {record.disease_name}",
                farm_id=crop.farm_id if crop else None,
                crop_id=record.crop_id,
                metadata_json=json.dumps(metadata)
            )

        # Log resolution if status changed to resolved
        if "status" in update_data and update_data["status"] == "resolved" and old_status != "resolved":
            await activity.log_activity(
                user_id=user_id,
                action="disease_resolved",
                entity_type="disease",
                entity_id=record.id,
                description=f"Resolved disease {record.disease_name}",
                farm_id=crop.farm_id if crop else None,
                crop_id=record.crop_id,
                metadata_json=json.dumps(metadata)
            )

        return DiseaseRecordResponse.model_validate(record)

    async def get_disease_info(self, disease_name: str) -> dict:
        """Get full disease info from the Knowledge Base."""
        result = await self.db.execute(
            select(DiseaseLibrary).where(DiseaseLibrary.disease_name.ilike(f"%{disease_name}%"))
        )
        disease = result.scalar_one_or_none()
        if not disease:
            raise NotFoundException("Disease", disease_name)
        
        return {
            "id": disease.id,
            "disease_name": disease.disease_name,
            "affected_crops": disease.affected_crops,
            "symptoms": disease.symptoms,
            "treatment": disease.treatment,
            "prevention": disease.prevention,
            "severity": disease.severity,
            "image_url": disease.image_url,
        }
