"""
AgriNova AI — Farm History Repository.

Cross-entity historical data access for V4 Personalized Intelligence.
Provides farm-level views spanning crops, fertilizer, irrigation,
disease records, and activity logs.
"""

from collections import defaultdict

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.activity_log import ActivityLog
from app.models.crop import Crop
from app.models.disease import DiseaseRecord
from app.models.fertilizer import FertilizerLog
from app.models.irrigation import IrrigationLog


class HistoryRepository:
    """Read-only, farm-scoped historical data access layer."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Internal helper: subquery of crop IDs belonging to a farm
    # ------------------------------------------------------------------

    def _farm_crop_ids(self, farm_id: str):
        """Return a scalar subquery of crop IDs for the given farm."""
        return select(Crop.id).where(Crop.farm_id == farm_id).scalar_subquery()

    # ------------------------------------------------------------------
    # 1. Crop history
    # ------------------------------------------------------------------

    async def get_crop_history(self, farm_id: str) -> list[Crop]:
        """Return historical crops for a farm, newest first.

        Includes harvested, abandoned, and active crops that carry
        meaningful history (variety, yield, dates).
        """
        result = await self.db.execute(
            select(Crop)
            .where(Crop.farm_id == farm_id)
            .order_by(Crop.planting_date.desc().nullslast(), Crop.created_at.desc())
        )
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # 2. Fertilizer history
    # ------------------------------------------------------------------

    async def get_fertilizer_history(
        self, farm_id: str, limit: int = 100
    ) -> list[dict]:
        """Return fertilizer applications across all crops of a farm.

        Uses a JOIN to include crop_name and avoid N+1 queries.
        Returns dicts so callers are decoupled from ORM internals.
        """
        stmt = (
            select(FertilizerLog, Crop.crop_name)
            .join(Crop, FertilizerLog.crop_id == Crop.id)
            .where(Crop.farm_id == farm_id)
            .order_by(FertilizerLog.date.desc(), FertilizerLog.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": log.id,
                "crop_id": log.crop_id,
                "crop_name": crop_name,
                "fertilizer_type": log.fertilizer_type,
                "quantity": log.quantity,
                "unit": log.unit,
                "date": log.date,
                "application_method": log.application_method,
                "growth_stage": log.growth_stage,
                "source": log.source,
                "observed_effect": log.observed_effect,
                "notes": log.notes,
            }
            for log, crop_name in rows
        ]

    # ------------------------------------------------------------------
    # 3. Irrigation history
    # ------------------------------------------------------------------

    async def get_irrigation_history(
        self, farm_id: str, limit: int = 100
    ) -> list[dict]:
        """Return irrigation records across all crops of a farm.

        Uses a JOIN to include crop_name and avoid N+1 queries.
        """
        stmt = (
            select(IrrigationLog, Crop.crop_name)
            .join(Crop, IrrigationLog.crop_id == Crop.id)
            .where(Crop.farm_id == farm_id)
            .order_by(IrrigationLog.date.desc(), IrrigationLog.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": log.id,
                "crop_id": log.crop_id,
                "crop_name": crop_name,
                "date": log.date,
                "water_amount_liters": log.water_amount_liters,
                "duration_minutes": log.duration_minutes,
                "method": log.method,
                "growth_stage": log.growth_stage,
                "source": log.source,
            }
            for log, crop_name in rows
        ]

    # ------------------------------------------------------------------
    # 4. Disease history
    # ------------------------------------------------------------------

    async def get_disease_history(
        self, farm_id: str, limit: int = 100
    ) -> list[dict]:
        """Return disease records across all crops of a farm.

        Uses a JOIN to include crop_name and avoid N+1 queries.
        """
        stmt = (
            select(DiseaseRecord, Crop.crop_name)
            .join(Crop, DiseaseRecord.crop_id == Crop.id)
            .where(Crop.farm_id == farm_id)
            .order_by(DiseaseRecord.detected_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "id": rec.id,
                "crop_id": rec.crop_id,
                "crop_name": crop_name,
                "disease_name": rec.disease_name,
                "severity": rec.severity,
                "symptoms_observed": rec.symptoms_observed,
                "treatment_applied": rec.treatment_applied,
                "outcome": rec.outcome,
                "status": rec.status,
                "detected_at": rec.detected_at,
                "resolved_at": rec.resolved_at,
            }
            for rec, crop_name in rows
        ]

    # ------------------------------------------------------------------
    # 5. Activity history
    # ------------------------------------------------------------------

    async def get_activity_history(
        self, farm_id: str, limit: int = 100
    ) -> list[dict]:
        """Return chronological ActivityLog entries for a farm."""
        stmt = (
            select(ActivityLog)
            .where(ActivityLog.farm_id == farm_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        logs = result.scalars().all()

        return [
            {
                "id": a.id,
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "crop_id": a.crop_id,
                "description": a.description,
                "metadata_json": a.metadata_json,
                "created_at": a.created_at,
            }
            for a in logs
        ]

    # ------------------------------------------------------------------
    # 6. Performance summary
    # ------------------------------------------------------------------

    async def get_farm_performance_summary(self, farm_id: str) -> dict:
        """Return aggregated historical metrics for a farm.

        Yield averages are grouped by unit to avoid mixing incompatible
        units (e.g. kg vs tons).
        """
        # --- Crop aggregates (single query) ---
        crop_stats = await self.db.execute(
            select(
                func.count(Crop.id).label("total_crops"),
                func.count(
                    case((Crop.status == "harvested", Crop.id))
                ).label("harvested_crops"),
                func.count(
                    case((Crop.status == "abandoned", Crop.id))
                ).label("abandoned_crops"),
                func.count(
                    case((Crop.yield_amount.isnot(None), Crop.id))
                ).label("crops_with_yield"),
            ).where(Crop.farm_id == farm_id)
        )
        cs = crop_stats.one()

        # --- Yield averages grouped by unit (safe: no cross-unit mixing) ---
        yield_by_unit_result = await self.db.execute(
            select(
                Crop.yield_unit,
                func.avg(Crop.yield_amount).label("avg_yield"),
                func.count(Crop.id).label("count"),
            )
            .where(
                Crop.farm_id == farm_id,
                Crop.yield_amount.isnot(None),
                Crop.yield_unit.isnot(None),
            )
            .group_by(Crop.yield_unit)
        )
        yield_by_unit = [
            {"unit": row.yield_unit, "avg_yield": round(row.avg_yield, 2), "count": row.count}
            for row in yield_by_unit_result.all()
        ]

        # --- Fertilizer count ---
        fert_count = await self.db.execute(
            select(func.count(FertilizerLog.id))
            .join(Crop, FertilizerLog.crop_id == Crop.id)
            .where(Crop.farm_id == farm_id)
        )
        total_fertilizer_applications = fert_count.scalar_one()

        # --- Irrigation count ---
        irr_count = await self.db.execute(
            select(func.count(IrrigationLog.id))
            .join(Crop, IrrigationLog.crop_id == Crop.id)
            .where(Crop.farm_id == farm_id)
        )
        total_irrigation_events = irr_count.scalar_one()

        # --- Disease counts ---
        disease_stats = await self.db.execute(
            select(
                func.count(DiseaseRecord.id).label("total"),
                func.count(
                    case((DiseaseRecord.status == "resolved", DiseaseRecord.id))
                ).label("resolved"),
                func.count(
                    case((DiseaseRecord.status == "active", DiseaseRecord.id))
                ).label("active"),
            )
            .join(Crop, DiseaseRecord.crop_id == Crop.id)
            .where(Crop.farm_id == farm_id)
        )
        ds = disease_stats.one()

        return {
            "total_crops": cs.total_crops,
            "harvested_crops": cs.harvested_crops,
            "abandoned_crops": cs.abandoned_crops,
            "crops_with_yield": cs.crops_with_yield,
            "yield_by_unit": yield_by_unit,
            "total_fertilizer_applications": total_fertilizer_applications,
            "total_irrigation_events": total_irrigation_events,
            "total_disease_records": ds.total,
            "resolved_disease_count": ds.resolved,
            "active_disease_count": ds.active,
        }
