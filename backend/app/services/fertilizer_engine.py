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
            fertilizer_type = "NPK 19:19:19"
            quantity_per_acre = 50.0
            unit = "kg"
            timing = "Morning"
            application_method = "Broadcasting"
            explanation = f"During {growth_stage}, {crop_name} benefits from NPK 19:19:19 at 50.0 kg/acre because it supports general growth."
        else:
            fertilizer_type = lib.fertilizer_type
            quantity_per_acre = lib.quantity_per_acre
            unit = lib.unit
            timing = lib.timing
            application_method = lib.application_method
            explanation = f"During {lib.stage_name}, {lib.crop_name} benefits from {lib.fertilizer_type} at {lib.quantity_per_acre} {lib.unit}/acre because it optimizes nutrient uptake."

        # V4 Phase 3: Deterministic Historical Personalization
        historically_adjusted = False
        personalization_rationale = None

        if historical_insights and historical_insights.input_usage:
            for usage in historical_insights.input_usage:
                if usage.crop_name.lower() == crop_name.lower() and usage.input_type.lower() != "irrigation":
                    # Rule 1: Check confidence. If low/None, do not personalize.
                    if usage.confidence is None or usage.confidence < 0.6:
                        continue
                        
                    # Rule 2: Determine proportional, bounded adjustment based on historical count.
                    # e.g., anything above 2 applications starts reducing the next recommendation.
                    excess_applications = max(0, usage.application_count - 2)
                    
                    if excess_applications > 0:
                        # Max bounded adjustment of 10% (0.10)
                        penalty_pct = min(0.10, excess_applications * 0.05)
                        
                        if penalty_pct > 0 and quantity_per_acre > 0:
                            # Do not let recommendation go to zero if originally positive
                            new_quantity = max(1.0, quantity_per_acre * (1.0 - penalty_pct))
                            quantity_per_acre = round(new_quantity, 2)
                            historically_adjusted = True
                            
                            pct_str = int(penalty_pct * 100)
                            personalization_rationale = f"Recommendation conservatively reduced by {pct_str}% based on repeated historical fertilizer usage for this crop (confidence: {usage.confidence:.2f})."
                    
                    break

        return {
            "fertilizer_type": fertilizer_type,
            "quantity_per_acre": quantity_per_acre,
            "unit": unit,
            "timing": timing,
            "application_method": application_method,
            "explanation": explanation,
            "historically_adjusted": historically_adjusted,
            "personalization_rationale": personalization_rationale
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
