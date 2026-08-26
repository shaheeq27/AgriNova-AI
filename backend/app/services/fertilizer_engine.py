"""
AgriNova AI — Fertilizer Engine service.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.knowledge import FertilizerLibrary
from app.models.fertilizer import FertilizerLog
from app.schemas.fertilizer import FertilizerLogCreate, FertilizerLogResponse
from app.ai.schemas.historical_analysis import HistoricalInsightsContext


class FertilizerEngine:
    async def get_recommendation(
        self, db: AsyncSession, crop_name: str, growth_stage: str, soil_type: str,
        historical_insights: HistoricalInsightsContext | None = None
    ) -> dict:
        result = await db.execute(
            select(FertilizerLibrary).where(
                FertilizerLibrary.crop_name.ilike(f"%{crop_name}%"),
                FertilizerLibrary.stage_name.ilike(f"%{growth_stage}%")
            )
        )
        lib = result.scalar_one_or_none()

        if not lib:
            # Fallback basic recommendation
            return {
                "fertilizer_type": "NPK 19:19:19",
                "quantity_per_acre": 50.0,
                "unit": "kg",
                "timing": "Morning",
                "application_method": "Broadcasting",
                "explanation": f"During {growth_stage}, {crop_name} benefits from NPK 19:19:19 at 50.0 kg/acre because it supports general growth."
            }

        explanation = f"During {lib.stage_name}, {lib.crop_name} benefits from {lib.fertilizer_type} at {lib.quantity_per_acre} {lib.unit}/acre because it optimizes nutrient uptake."
        
        return {
            "fertilizer_type": lib.fertilizer_type,
            "quantity_per_acre": lib.quantity_per_acre,
            "unit": lib.unit,
            "timing": lib.timing,
            "application_method": lib.application_method,
            "explanation": explanation
        }

    async def log_application(
        self, db: AsyncSession, user_id: str, crop_id: str, data: FertilizerLogCreate
    ) -> FertilizerLogResponse:
        from app.models.crop import Crop
        from app.services.activity_service import ActivityService
        import json

        # Get crop to find farm_id
        crop_result = await db.execute(select(Crop).where(Crop.id == crop_id))
        crop = crop_result.scalar_one_or_none()
        if not crop:
            raise ValueError(f"Crop not found: {crop_id}")
            
        log = FertilizerLog(
            crop_id=crop_id,
            date=data.date,
            fertilizer_type=data.fertilizer_type,
            quantity=data.quantity,
            unit=data.unit,
            application_method=data.application_method,
            growth_stage=data.growth_stage,
            notes=data.notes,
            source="manual"
        )
        db.add(log)
        await db.flush()
        await db.refresh(log)

        # Log activity
        activity_service = ActivityService(db)
        metadata = {
            "fertilizer_type": data.fertilizer_type,
            "quantity": data.quantity,
            "unit": data.unit,
            "application_method": data.application_method,
            "growth_stage": data.growth_stage,
            "source": "manual",
            "date": data.date.isoformat() if data.date else None
        }
        await activity_service.log_activity(
            user_id=user_id,
            action="fertilizer_applied",
            entity_type="fertilizer",
            entity_id=log.id,
            description=f"Applied {data.fertilizer_type} to crop",
            farm_id=crop.farm_id,
            crop_id=crop_id,
            metadata_json=json.dumps(metadata)
        )

        return FertilizerLogResponse.model_validate(log)

    async def get_logs(self, db: AsyncSession, crop_id: str) -> list[FertilizerLogResponse]:
        result = await db.execute(
            select(FertilizerLog)
            .where(FertilizerLog.crop_id == crop_id)
            .order_by(FertilizerLog.date.desc())
        )
        logs = result.scalars().all()
        return [FertilizerLogResponse.model_validate(log) for log in logs]
