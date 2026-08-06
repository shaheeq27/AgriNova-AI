"""
AgriNova AI — Report generation service.

Assembles structured reports from existing data across repositories.
No new tables — pure aggregation from Crops, Farms, Weather, Fertilizer,
Irrigation, Timeline, DailyTask, Disease, and ActivityLog tables.
"""

from datetime import date, datetime, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.crop import Crop
from app.models.disease import DiseaseRecord
from app.models.farm import Farm
from app.models.fertilizer import FertilizerLog
from app.models.irrigation import IrrigationLog
from app.models.timeline import CropTimeline, DailyTask
from app.models.weather import WeatherRecord


class ReportService:
    """Generates structured farm operation reports."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── helpers ──────────────────────────────────────────────

    def _meta(self, report_type: str, period_start: str | None = None, period_end: str | None = None) -> dict:
        return {
            "report_type": report_type,
            "generated_at": datetime.now(timezone.utc),
            "period_start": period_start,
            "period_end": period_end,
        }

    async def _verify_farm_ownership(self, user_id: str, farm_id: str) -> Farm:
        result = await self.db.execute(select(Farm).where(Farm.id == farm_id))
        farm = result.scalar_one_or_none()
        if not farm:
            raise NotFoundException("Farm", farm_id)
        if farm.user_id != user_id:
            raise ForbiddenException("You do not have access to this farm")
        return farm

    async def _verify_crop_ownership(self, user_id: str, crop_id: str) -> Crop:
        result = await self.db.execute(select(Crop).where(Crop.id == crop_id))
        crop = result.scalar_one_or_none()
        if not crop:
            raise NotFoundException("Crop", crop_id)
        farm = await self._verify_farm_ownership(user_id, crop.farm_id)
        return crop

    # ── Crop Report ──────────────────────────────────────────

    async def generate_crop_report(self, user_id: str, crop_id: str) -> dict:
        """Generate a comprehensive report for a single crop."""

        crop = await self._verify_crop_ownership(user_id, crop_id)

        # Farm name
        farm_res = await self.db.execute(select(Farm.name).where(Farm.id == crop.farm_id))
        farm_name = farm_res.scalar() or "Unknown"

        # Timeline summary
        stage_res = await self.db.execute(
            select(
                func.count(CropTimeline.id),
                func.sum(case((CropTimeline.status == "completed", 1), else_=0)),
            ).where(CropTimeline.crop_id == crop_id)
        )
        total_stages, completed_stages = stage_res.first()
        total_stages = total_stages or 0
        completed_stages = int(completed_stages or 0)

        active_stage_res = await self.db.execute(
            select(CropTimeline.stage_name)
            .where(CropTimeline.crop_id == crop_id, CropTimeline.status == "active")
            .limit(1)
        )
        active_stage = active_stage_res.scalar()

        progress = (completed_stages / total_stages * 100.0) if total_stages > 0 else 0.0

        # Tasks summary
        task_res = await self.db.execute(
            select(
                func.count(DailyTask.id),
                func.sum(case((DailyTask.is_completed == True, 1), else_=0)),
            ).where(DailyTask.crop_id == crop_id)
        )
        total_tasks, completed_tasks = task_res.first()
        total_tasks = total_tasks or 0
        completed_tasks = int(completed_tasks or 0)

        overdue_res = await self.db.execute(
            select(func.count(DailyTask.id)).where(
                DailyTask.crop_id == crop_id,
                DailyTask.is_completed == False,
                DailyTask.scheduled_date < date.today(),
            )
        )
        overdue = overdue_res.scalar() or 0

        task_pct = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0

        # Disease count
        disease_res = await self.db.execute(
            select(func.count(DiseaseRecord.id)).where(DiseaseRecord.crop_id == crop_id)
        )
        disease_count = disease_res.scalar() or 0

        # Fertilizer applications
        fert_res = await self.db.execute(
            select(func.count(FertilizerLog.id)).where(FertilizerLog.crop_id == crop_id)
        )
        fert_count = fert_res.scalar() or 0

        # Irrigation applications
        irrig_res = await self.db.execute(
            select(func.count(IrrigationLog.id)).where(IrrigationLog.crop_id == crop_id)
        )
        irrig_count = irrig_res.scalar() or 0

        return {
            "meta": self._meta("crop_report"),
            "data": {
                "crop_id": crop.id,
                "crop_name": crop.crop_name,
                "farm_name": farm_name,
                "status": crop.status,
                "season": crop.season,
                "planting_date": crop.planting_date.isoformat() if crop.planting_date else None,
                "expected_harvest_date": crop.expected_harvest_date.isoformat() if crop.expected_harvest_date else None,
                "area_acres": crop.area_acres,
                "timeline": {
                    "total_stages": total_stages,
                    "completed_stages": completed_stages,
                    "active_stage": active_stage,
                    "progress_percent": round(progress, 2),
                },
                "tasks": {
                    "total": total_tasks,
                    "completed": completed_tasks,
                    "overdue": overdue,
                    "completion_percent": round(task_pct, 2),
                },
                "disease_count": disease_count,
                "fertilizer_applications": fert_count,
                "irrigation_applications": irrig_count,
            },
        }

    # ── Farm Report ──────────────────────────────────────────

    async def generate_farm_report(self, user_id: str, farm_id: str) -> dict:
        """Generate a comprehensive report for a farm."""

        farm = await self._verify_farm_ownership(user_id, farm_id)

        # Crop summaries
        crops_res = await self.db.execute(select(Crop).where(Crop.farm_id == farm_id))
        crops = crops_res.scalars().all()

        crop_summaries = []
        active_count = 0
        harvested_count = 0
        total_tasks = 0
        total_completed = 0

        for crop in crops:
            if crop.status == "active":
                active_count += 1
            elif crop.status == "harvested":
                harvested_count += 1

            task_res = await self.db.execute(
                select(
                    func.count(DailyTask.id),
                    func.sum(case((DailyTask.is_completed == True, 1), else_=0)),
                ).where(DailyTask.crop_id == crop.id)
            )
            ct, cc = task_res.first()
            ct = ct or 0
            cc = int(cc or 0)
            total_tasks += ct
            total_completed += cc

            health = (cc / ct * 100.0) if ct > 0 else 100.0
            crop_summaries.append({
                "crop_id": crop.id,
                "crop_name": crop.crop_name,
                "status": crop.status,
                "health_score": round(health, 2),
            })

        # Disease records
        disease_res = await self.db.execute(
            select(func.count(DiseaseRecord.id))
            .join(Crop)
            .where(Crop.farm_id == farm_id)
        )
        total_diseases = disease_res.scalar() or 0

        # Activity count (if table exists — safe fallback)
        total_activities = 0
        try:
            from app.models.activity_log import ActivityLog
            act_res = await self.db.execute(
                select(func.count(ActivityLog.id)).where(ActivityLog.farm_id == farm_id)
            )
            total_activities = act_res.scalar() or 0
        except Exception:
            pass

        return {
            "meta": self._meta("farm_report"),
            "data": {
                "farm_id": farm.id,
                "farm_name": farm.name,
                "location": farm.location_city,
                "total_area_acres": farm.total_area_acres,
                "soil_type": farm.soil_type,
                "total_crops": len(crops),
                "active_crops": active_count,
                "harvested_crops": harvested_count,
                "crop_summaries": crop_summaries,
                "total_tasks": total_tasks,
                "completed_tasks": total_completed,
                "total_disease_records": total_diseases,
                "total_activities": total_activities,
            },
        }

    # ── Weather Report ───────────────────────────────────────

    async def generate_weather_report(self, user_id: str, farm_id: str, days: int = 30) -> dict:
        """Generate a weather report for a farm over the specified period."""

        farm = await self._verify_farm_ownership(user_id, farm_id)

        today = date.today()
        from datetime import timedelta
        start_date = today - timedelta(days=days)

        result = await self.db.execute(
            select(WeatherRecord)
            .where(
                WeatherRecord.farm_id == farm_id,
                WeatherRecord.date >= start_date,
            )
            .order_by(WeatherRecord.date.asc())
        )
        records = result.scalars().all()

        entries = []
        temps = []
        total_rain = 0.0

        for rec in records:
            entries.append({
                "date": rec.date.isoformat() if rec.date else "",
                "temp_avg": rec.temp_avg,
                "humidity": rec.humidity,
                "rainfall": rec.rainfall,
                "condition": rec.condition,
            })
            if rec.temp_avg is not None:
                temps.append(rec.temp_avg)
            if rec.rainfall is not None:
                total_rain += rec.rainfall

        avg_temp = sum(temps) / len(temps) if temps else None

        return {
            "meta": self._meta(
                "weather_report",
                period_start=start_date.isoformat(),
                period_end=today.isoformat(),
            ),
            "data": {
                "farm_id": farm.id,
                "farm_name": farm.name,
                "entries": entries,
                "avg_temperature": round(avg_temp, 2) if avg_temp is not None else None,
                "total_rainfall": round(total_rain, 2),
                "alert_count": 0,
            },
        }

    # ── Fertilizer Report ────────────────────────────────────

    async def generate_fertilizer_report(self, user_id: str, crop_id: str) -> dict:
        """Generate a fertilizer application report for a crop."""

        crop = await self._verify_crop_ownership(user_id, crop_id)

        result = await self.db.execute(
            select(FertilizerLog)
            .where(FertilizerLog.crop_id == crop_id)
            .order_by(FertilizerLog.date.asc())
        )
        logs = result.scalars().all()

        entries = []
        for log in logs:
            entries.append({
                "date": log.date.isoformat() if log.date else "",
                "fertilizer_type": log.fertilizer_type,
                "quantity": log.quantity,
                "growth_stage": log.growth_stage if hasattr(log, "growth_stage") else None,
            })

        return {
            "meta": self._meta("fertilizer_report"),
            "data": {
                "crop_id": crop.id,
                "crop_name": crop.crop_name,
                "entries": entries,
                "total_applications": len(entries),
            },
        }

    # ── Irrigation Report ────────────────────────────────────

    async def generate_irrigation_report(self, user_id: str, crop_id: str) -> dict:
        """Generate an irrigation application report for a crop."""

        crop = await self._verify_crop_ownership(user_id, crop_id)

        result = await self.db.execute(
            select(IrrigationLog)
            .where(IrrigationLog.crop_id == crop_id)
            .order_by(IrrigationLog.date.asc())
        )
        logs = result.scalars().all()

        entries = []
        total_water = 0.0
        for log in logs:
            water = log.water_amount_liters if hasattr(log, "water_amount_liters") else None
            entries.append({
                "date": log.date.isoformat() if log.date else "",
                "water_amount_liters": water,
                "duration_minutes": log.duration_minutes if hasattr(log, "duration_minutes") else None,
                "method": log.method if hasattr(log, "method") else None,
            })
            if water:
                total_water += water

        return {
            "meta": self._meta("irrigation_report"),
            "data": {
                "crop_id": crop.id,
                "crop_name": crop.crop_name,
                "entries": entries,
                "total_applications": len(entries),
                "total_water_liters": round(total_water, 2),
            },
        }
