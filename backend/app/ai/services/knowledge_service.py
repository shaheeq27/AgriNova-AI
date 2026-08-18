"""
AgriNova AI — Knowledge Service (Structured RAG).

Retrieves relevant agricultural knowledge from the AgriNova KB
and assembles it into ``RAGContext`` for injection into the AI prompt.

This is **deterministic structured retrieval**, not vector-search RAG:
  - Retrieval is scoped to the farmer's actual crops (from Phase 3).
  - Irrigation guidelines are further filtered by the farm's soil type.
  - Disease matching uses exact comparison on the comma-separated
    ``affected_crops`` field (no SQL LIKE).

Safety rule:
  If a fertilizer quantity, pesticide dosage, irrigation amount, or
  chemical application is not present in the retrieved knowledge,
  it must NOT be invented.  The ``CropKnowledge`` summary will simply
  omit the missing data.
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas.context import CropKnowledge, RAGContext
from app.repositories.knowledge_repo import KnowledgeRepository

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Builds ``RAGContext`` from the AgriNova knowledge base."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = KnowledgeRepository(db)

    async def build_knowledge_context(
        self,
        crop_names: list[str],
        soil_type: str | None = None,
    ) -> RAGContext:
        """Retrieve KB knowledge for the farmer's crops.

        Args:
            crop_names: List of crop names the farmer is growing.
            soil_type: The farm's soil type (for irrigation filtering).

        Returns:
            ``RAGContext`` with one ``CropKnowledge`` per crop.
            Missing KB entries produce empty fields, never errors.
        """
        if not crop_names:
            return RAGContext()

        try:
            # Bulk queries — one per category, not per crop
            profiles = await self.repo.get_crop_profiles(crop_names)
            stages = await self.repo.get_growth_stages(crop_names)
            all_diseases = await self.repo.get_all_diseases()
            fertilizers = await self.repo.get_fertilizer_guidelines(crop_names)
            irrigation = await self.repo.get_irrigation_guidelines(
                crop_names, soil_type
            )
        except Exception:
            logger.warning(
                "Failed to query knowledge base", exc_info=True
            )
            return RAGContext()

        # Index by crop_name for O(1) lookup
        profile_map = {p.crop_name: p for p in profiles}
        stage_map: dict[str, list] = {}
        for s in stages:
            stage_map.setdefault(s.crop_name, []).append(s)
        fert_map: dict[str, list] = {}
        for f in fertilizers:
            fert_map.setdefault(f.crop_name, []).append(f)
        irrig_map: dict[str, list] = {}
        for ig in irrigation:
            irrig_map.setdefault(ig.crop_name, []).append(ig)

        # Disease matching: exact comparison on comma-separated field
        disease_map: dict[str, list] = {}
        crop_names_lower = {c.strip().lower() for c in crop_names}
        for d in all_diseases:
            affected = {
                c.strip().lower() for c in d.affected_crops.split(",")
            }
            matched_crops = affected & crop_names_lower
            for crop_lower in matched_crops:
                # Find the original-cased crop name
                original = next(
                    (c for c in crop_names if c.strip().lower() == crop_lower),
                    crop_lower,
                )
                disease_map.setdefault(original, []).append(d)

        # Assemble CropKnowledge per crop
        crop_knowledge: list[CropKnowledge] = []
        for crop_name in crop_names:
            ck = self._build_crop_knowledge(
                crop_name,
                profile=profile_map.get(crop_name),
                stages=stage_map.get(crop_name, []),
                diseases=disease_map.get(crop_name, []),
                fertilizers=fert_map.get(crop_name, []),
                irrigation_guides=irrig_map.get(crop_name, []),
            )
            crop_knowledge.append(ck)

        return RAGContext(crop_knowledge=crop_knowledge)

    # ── Private helpers ──────────────────────────────────────────────────

    @staticmethod
    def _build_crop_knowledge(
        crop_name: str,
        profile,
        stages: list,
        diseases: list,
        fertilizers: list,
        irrigation_guides: list,
    ) -> CropKnowledge:
        """Assemble a single ``CropKnowledge`` from raw ORM records."""

        # Profile
        profile_description = None
        ideal_conditions = None
        if profile:
            profile_description = profile.description
            parts = [
                f"Temp: {profile.temp_min}–{profile.temp_max}°C",
                f"Rain: {profile.rain_min}–{profile.rain_max}mm",
                f"Humidity: {profile.humidity_min}–{profile.humidity_max}%",
                f"Soil: {profile.ideal_soil_types}",
            ]
            if profile.ideal_ph_min is not None and profile.ideal_ph_max is not None:
                parts.append(f"pH: {profile.ideal_ph_min}–{profile.ideal_ph_max}")
            if profile.growing_season:
                parts.append(f"Season: {profile.growing_season}")
            if profile.total_duration_days:
                parts.append(f"Duration: {profile.total_duration_days} days")
            ideal_conditions = " | ".join(parts)

        # Growth stages
        growth_stage_summaries = []
        for s in stages:
            summary = f"{s.stage_name} ({s.duration_days} days)"
            if s.description:
                summary += f": {s.description}"
            growth_stage_summaries.append(summary)

        # Diseases
        disease_summaries = []
        for d in diseases:
            summary = f"{d.disease_name} [{d.severity}]: {d.symptoms}"
            disease_summaries.append(summary)

        # Fertilizer schedule
        fert_summaries = []
        for f in fertilizers:
            summary = (
                f"{f.stage_name}: {f.fertilizer_type} "
                f"{f.quantity_per_acre} {f.unit}/acre, {f.timing}"
            )
            if f.application_method:
                summary += f" ({f.application_method})"
            fert_summaries.append(summary)

        # Irrigation guidelines
        irrig_summaries = []
        for ig in irrigation_guides:
            summary = (
                f"{ig.stage_name}: {ig.water_requirement_mm}mm, "
                f"{ig.frequency}"
            )
            if ig.method:
                summary += f" ({ig.method})"
            irrig_summaries.append(summary)

        return CropKnowledge(
            crop_name=crop_name,
            profile_description=profile_description,
            ideal_conditions=ideal_conditions,
            growth_stages=growth_stage_summaries,
            diseases=disease_summaries,
            fertilizer_schedule=fert_summaries,
            irrigation_guidelines=irrig_summaries,
        )
