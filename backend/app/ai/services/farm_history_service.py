"""
AgriNova AI — Farm History Service.

Transforms raw historical data from the HistoryRepository into
a structured FarmHistoryContext suitable for AI processing.
"""

from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas.context import CropHistoryEntry, FarmHistoryContext
from app.repositories.history_repo import HistoryRepository


class FarmHistoryService:
    """Transforms repository data into structured AI context."""

    def __init__(self, db: AsyncSession):
        self.repo = HistoryRepository(db)

    async def build_history_context(
        self, farm_id: str, *, limit: int = 10
    ) -> FarmHistoryContext:
        """
        Retrieve and transform historical data into FarmHistoryContext.
        Handles empty farms safely without throwing.
        """
        
        # 1. Fetch raw data
        crops = await self.repo.get_crop_history(farm_id)
        
        # If no crops exist, there is no history. Safe early return.
        if not crops:
            return FarmHistoryContext()

        # Fetch other entities to calculate per-crop counts without N+1
        # We fetch without strict limits here just for counting, or we could
        # fetch with a high limit. Let us just use a reasonably high limit
        # to ensure we get accurate counts without unbounded memory.
        ferts = await self.repo.get_fertilizer_history(farm_id, limit=500)
        irrs = await self.repo.get_irrigation_history(farm_id, limit=500)
        
        fert_counts = defaultdict(int)
        for f in ferts:
            fert_counts[f["crop_id"]] += 1
            
        irr_counts = defaultdict(int)
        for i in irrs:
            irr_counts[i["crop_id"]] += 1
            
        # For diseases, fetch a larger batch for counting if limit is small,
        # but slice it for the summary.
        all_diseases = await self.repo.get_disease_history(farm_id, limit=100)
        disease_counts = defaultdict(int)
        for d in all_diseases:
            disease_counts[d["crop_id"]] += 1
            
        # 2. Build Crop History Entries
        past_crops = []
        # We only take up to `limit` crops to avoid blowing up context
        for crop in crops[:limit]:
            entry = CropHistoryEntry(
                crop_name=crop.crop_name,
                variety=crop.variety,
                season=crop.season,
                planting_date=crop.planting_date,
                harvest_date=crop.actual_harvest_date,
                yield_amount=crop.yield_amount,
                yield_unit=crop.yield_unit,
                status=crop.status,
                disease_count=disease_counts[crop.id],
                fertilizer_applications=fert_counts[crop.id],
                irrigation_applications=irr_counts[crop.id],
            )
            past_crops.append(entry)

        # 3. Build Recent Disease Summary
        recent_diseases = []
        for d in all_diseases[:limit]:
            summary_parts = [f"{d['disease_name']}"]
            if d.get("severity"):
                summary_parts.append(f"{d['severity']} severity")
            if d.get("status"):
                summary_parts.append(f"{d['status']}")
            if d.get("treatment_applied"):
                summary_parts.append(f"treatment: {d['treatment_applied']}")
            if d.get("outcome"):
                summary_parts.append(f"outcome: {d['outcome']}")
                
            recent_diseases.append(" — ".join(summary_parts))

        # 4. Seasonal Patterns
        season_to_crops = defaultdict(set)
        for crop in crops: # use all crops for accurate patterns
            if crop.season and crop.crop_name:
                season_to_crops[crop.season].add(crop.crop_name)
                
        seasonal_patterns = []
        for season, c_names in sorted(season_to_crops.items()):
            seasonal_patterns.append(f"{season}: {', '.join(sorted(list(c_names)))}")

        # 5. Performance Summary
        perf_stats = await self.repo.get_farm_performance_summary(farm_id)
        
        perf_lines = []
        perf_lines.append(f"{perf_stats['total_crops']} recorded crops; {perf_stats['harvested_crops']} harvested and {perf_stats['abandoned_crops']} abandoned.")
        perf_lines.append(f"{perf_stats['crops_with_yield']} crops have recorded yields.")
        perf_lines.append(f"{perf_stats['total_fertilizer_applications']} fertilizer applications and {perf_stats['total_irrigation_events']} irrigation events recorded.")
        perf_lines.append(f"{perf_stats['total_disease_records']} disease records: {perf_stats['resolved_disease_count']} resolved, {perf_stats['active_disease_count']} active.")
        
        if perf_stats['yield_by_unit']:
            yield_parts = []
            for y in perf_stats['yield_by_unit']:
                yield_parts.append(f"{y['avg_yield']} {y['unit']} across {y['count']} crop{'s' if y['count'] != 1 else ''}")
            perf_lines.append(f"Average recorded yield: {' and '.join(yield_parts)}.")

        performance_summary = "\n".join(perf_lines)

        return FarmHistoryContext(
            past_crops=past_crops,
            recent_diseases=recent_diseases,
            seasonal_patterns=seasonal_patterns,
            performance_summary=performance_summary
        )
