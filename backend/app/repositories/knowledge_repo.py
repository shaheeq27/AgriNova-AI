"""
AgriNova AI — Knowledge Base repository.

Centralised data-access layer for the curated knowledge tables:

  - ``kb_crop_profiles``
  - ``kb_growth_stages``
  - ``kb_disease_library``
  - ``kb_fertilizer_library``
  - ``kb_irrigation_guidelines``

All query methods accept a **list** of crop names to enable bulk
retrieval and avoid N+1 queries when a farm has multiple crops.

Disease matching uses in-Python exact comparison (not SQL LIKE) to
prevent false positives on the comma-separated ``affected_crops``
column.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import (
    CropProfile,
    DiseaseLibrary,
    FertilizerLibrary,
    GrowthStage,
    IrrigationGuideline,
)


class KnowledgeRepository:
    """Data access for the AgriNova curated knowledge base."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Crop Profiles ────────────────────────────────────────────────────

    async def get_crop_profiles(
        self, crop_names: list[str]
    ) -> list[CropProfile]:
        """Fetch crop profiles for the given crop names."""
        if not crop_names:
            return []
        result = await self.db.execute(
            select(CropProfile).where(CropProfile.crop_name.in_(crop_names))
        )
        return list(result.scalars().all())

    # ── Growth Stages ────────────────────────────────────────────────────

    async def get_growth_stages(
        self, crop_names: list[str]
    ) -> list[GrowthStage]:
        """Fetch growth stages for the given crop names, ordered."""
        if not crop_names:
            return []
        result = await self.db.execute(
            select(GrowthStage)
            .where(GrowthStage.crop_name.in_(crop_names))
            .order_by(GrowthStage.crop_name, GrowthStage.stage_order)
        )
        return list(result.scalars().all())

    # ── Disease Library ──────────────────────────────────────────────────

    async def get_all_diseases(self) -> list[DiseaseLibrary]:
        """Fetch all disease entries.

        Filtering by crop is done in Python (exact match on the
        comma-separated ``affected_crops`` field) to avoid LIKE
        false positives.
        """
        result = await self.db.execute(
            select(DiseaseLibrary).order_by(DiseaseLibrary.disease_name)
        )
        return list(result.scalars().all())

    # ── Fertilizer Library ───────────────────────────────────────────────

    async def get_fertilizer_guidelines(
        self, crop_names: list[str]
    ) -> list[FertilizerLibrary]:
        """Fetch fertilizer guidelines for the given crop names."""
        if not crop_names:
            return []
        result = await self.db.execute(
            select(FertilizerLibrary)
            .where(FertilizerLibrary.crop_name.in_(crop_names))
            .order_by(FertilizerLibrary.crop_name, FertilizerLibrary.stage_name)
        )
        return list(result.scalars().all())

    # ── Irrigation Guidelines ────────────────────────────────────────────

    async def get_irrigation_guidelines(
        self, crop_names: list[str], soil_type: str | None = None
    ) -> list[IrrigationGuideline]:
        """Fetch irrigation guidelines for the given crop names.

        If ``soil_type`` is provided, results are further filtered
        to match the farm's soil.
        """
        if not crop_names:
            return []
        stmt = (
            select(IrrigationGuideline)
            .where(IrrigationGuideline.crop_name.in_(crop_names))
        )
        if soil_type:
            stmt = stmt.where(IrrigationGuideline.soil_type == soil_type)
        stmt = stmt.order_by(
            IrrigationGuideline.crop_name, IrrigationGuideline.stage_name
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
