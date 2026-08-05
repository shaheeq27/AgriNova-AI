"""
AgriNova AI — Irrigation Engine service.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.knowledge import IrrigationGuideline
from app.models.irrigation import IrrigationLog
from app.schemas.irrigation import IrrigationLogCreate, IrrigationLogResponse


class IrrigationEngine:
    async def get_recommendation(
        self, db: AsyncSession, crop_name: str, growth_stage: str, soil_type: str, current_weather: dict | None = None
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
            rainfall = current_weather.get("rainfall", 0.0)
            temp = current_weather.get("temperature", 25.0)
            humidity = current_weather.get("humidity", 50.0)

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

        return {
            "water_requirement_mm": water_req,
            "frequency": freq,
            "method": method,
            "explanation": explanation,
            "weather_adjusted": weather_adjusted
        }

    async def log_irrigation(
        self, db: AsyncSession, crop_id: str, data: IrrigationLogCreate
    ) -> IrrigationLogResponse:
        log = IrrigationLog(
            crop_id=crop_id,
            date=data.date,
            water_amount_liters=data.water_amount_liters,
            duration_minutes=data.duration_minutes,
            method=data.method,
            notes=data.notes,
            source="manual"
        )
        db.add(log)
        await db.flush()
        await db.refresh(log)
        return IrrigationLogResponse.model_validate(log)

    async def get_logs(self, db: AsyncSession, crop_id: str) -> list[IrrigationLogResponse]:
        result = await db.execute(
            select(IrrigationLog)
            .where(IrrigationLog.crop_id == crop_id)
            .order_by(IrrigationLog.date.desc())
        )
        logs = result.scalars().all()
        return [IrrigationLogResponse.model_validate(log) for log in logs]
