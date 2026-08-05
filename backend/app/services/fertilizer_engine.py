"""
AgriNova AI — Fertilizer Engine service.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.knowledge import FertilizerLibrary
from app.models.fertilizer import FertilizerLog
from app.schemas.fertilizer import FertilizerLogCreate, FertilizerLogResponse


class FertilizerEngine:
    async def get_recommendation(
        self, db: AsyncSession, crop_name: str, growth_stage: str, soil_type: str
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
        self, db: AsyncSession, crop_id: str, data: FertilizerLogCreate
    ) -> FertilizerLogResponse:
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
        return FertilizerLogResponse.model_validate(log)

    async def get_logs(self, db: AsyncSession, crop_id: str) -> list[FertilizerLogResponse]:
        result = await db.execute(
            select(FertilizerLog)
            .where(FertilizerLog.crop_id == crop_id)
            .order_by(FertilizerLog.date.desc())
        )
        logs = result.scalars().all()
        return [FertilizerLogResponse.model_validate(log) for log in logs]
