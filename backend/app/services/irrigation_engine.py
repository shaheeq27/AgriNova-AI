"""
AgriNova AI — Irrigation Engine service.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.knowledge import IrrigationGuideline
from app.models.irrigation import IrrigationLog
from app.schemas.irrigation import IrrigationLogCreate, IrrigationLogResponse
from app.ai.schemas.historical_analysis import HistoricalInsightsContext


class IrrigationEngine:
    async def get_recommendation(
        self, db: AsyncSession, crop_name: str, growth_stage: str, soil_type: str, current_weather: dict | None = None,
        historical_insights: HistoricalInsightsContext | None = None
    ) -> dict:
        result = await db.execute(
            select(IrrigationGuideline).where(
                IrrigationGuideline.crop_name.ilike(f"%{crop_name}%"),
                IrrigationGuideline.stage_name.ilike(f"%{growth_stage}%"),
                IrrigationGuideline.soil_type.ilike(f"%{soil_type}%")
            )
        )
        guide = result.scalar_one_or_none()

        if guide:
            water_req = guide.water_requirement_mm
            freq = guide.frequency
            method = guide.method
        else:
            water_req = 20.0
            freq = "Every 3 days"
            method = "Drip"

        explanation = f"Base recommendation for {crop_name} in {soil_type} soil during {growth_stage} stage."
        weather_adjusted = False

        if current_weather:
            rainfall = current_weather.get("rainfall")
            if rainfall is None:
                rainfall = 0.0

            temp = current_weather.get("temperature")
            if temp is None:
                temp = 25.0

            humidity = current_weather.get("humidity")
            if humidity is None:
                humidity = 50.0

            if rainfall > 20.0:
                explanation = "Skip irrigation today - sufficient rainfall received."
                water_req = 0.0
                weather_adjusted = True
            else:
                if temp > 35.0:
                    freq = "Daily"
                    explanation += " Increased frequency due to high temperature."
                    weather_adjusted = True
                if humidity > 80.0:
                    water_req *= 0.8
                    explanation += " Reduced amount due to high humidity."
                    weather_adjusted = True

        # V4 Phase 3: Deterministic Historical Personalization
        historically_adjusted = False
        personalization_rationale = None

        if historical_insights and historical_insights.input_usage:
            for usage in historical_insights.input_usage:
                if usage.crop_name.lower() == crop_name.lower() and usage.input_type.lower() == "irrigation":
                    # Rule 1: Check confidence
                    if usage.confidence is None or usage.confidence < 0.6:
                        continue

                    # Rule 2: Determine proportional, bounded adjustment
                    # e.g., anything above 4 irrigations starts reducing the next recommendation.
                    excess_applications = max(0, usage.application_count - 4)

                    if excess_applications > 0:
                        # Max bounded adjustment of 10% (0.10)
                        penalty_pct = min(0.10, excess_applications * 0.05)

                        if penalty_pct > 0 and water_req > 0:
                            new_water_req = max(1.0, water_req * (1.0 - penalty_pct))
                            water_req = round(new_water_req, 2)
                            historically_adjusted = True

                            pct_str = int(penalty_pct * 100)
                            personalization_rationale = f"Recommendation conservatively reduced by {pct_str}% based on repeated historical irrigation usage for this crop (confidence: {usage.confidence:.2f})."

                    break

        return {
            "water_requirement_mm": water_req,
            "frequency": freq,
            "method": method,
            "explanation": explanation,
            "weather_adjusted": weather_adjusted,
            "historically_adjusted": historically_adjusted,
            "personalization_rationale": personalization_rationale
        }

    async def log_irrigation(
        self, db: AsyncSession, user_id: str, crop_id: str, data: IrrigationLogCreate
    ) -> IrrigationLogResponse:
        from app.models.crop import Crop
        from app.services.activity_service import ActivityService
        import json

        # Get crop to find farm_id
        crop_result = await db.execute(select(Crop).where(Crop.id == crop_id))
        crop = crop_result.scalar_one_or_none()
        if not crop:
            raise ValueError(f"Crop not found: {crop_id}")

        log = IrrigationLog(
            crop_id=crop_id,
            date=data.date,
            water_amount_liters=data.water_amount_liters,
            duration_minutes=data.duration_minutes,
            method=data.method,
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
            "water_amount_liters": data.water_amount_liters,
            "duration_minutes": data.duration_minutes,
            "method": data.method,
            "growth_stage": data.growth_stage,
            "source": "manual",
            "date": data.date.isoformat() if data.date else None
        }
        await activity_service.log_activity(
            user_id=user_id,
            action="irrigation_performed",
            entity_type="irrigation",
            entity_id=log.id,
            description=f"Irrigated crop",
            farm_id=crop.farm_id,
            crop_id=crop_id,
            metadata_json=json.dumps(metadata)
        )

        return IrrigationLogResponse.model_validate(log)

    async def get_logs(self, db: AsyncSession, crop_id: str) -> list[IrrigationLogResponse]:
        result = await db.execute(
            select(IrrigationLog)
            .where(IrrigationLog.crop_id == crop_id)
            .order_by(IrrigationLog.date.desc())
        )
        logs = result.scalars().all()
        return [IrrigationLogResponse.model_validate(log) for log in logs]
