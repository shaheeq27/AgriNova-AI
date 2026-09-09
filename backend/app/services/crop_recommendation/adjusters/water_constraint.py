"""
AgriNova AI — Water Constraint Adjuster.
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.knowledge import IrrigationGuideline
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker

class WaterConstraintAdjuster:
    """
    Adjusts or filters crops based on farm water availability.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def apply(self, trackers: list[AdjustmentTracker], context: RecommendationContext):
        if not context.water_source:
            return
            
        water_source = context.water_source.strip().lower()
        if water_source not in ["none", "rainfed"]:
            # No water constraints for farms with irrigation
            return
            
        # Get water requirements for all candidates
        crop_names = [t.crop.crop_name for t in trackers if not t.is_filtered]
        if not crop_names:
            return
            
        # We need total water requirement per crop for the specific farm soil type
        # Note: the 300mm/500mm thresholds below are provisional policy parameters
        # and should be made configurable in future versions.
        stmt = (
            select(
                IrrigationGuideline.crop_name,
                func.sum(IrrigationGuideline.water_requirement_mm).label("total_water")
            )
            .where(
                IrrigationGuideline.crop_name.in_(crop_names),
                IrrigationGuideline.soil_type == context.soil_type
            )
            .group_by(IrrigationGuideline.crop_name)
        )
        
        result = await self.db.execute(stmt)
        water_reqs = {row.crop_name: float(row.total_water) for row in result.all()}

        for tracker in trackers:
            if tracker.is_filtered:
                continue
                
            req = water_reqs.get(tracker.crop.crop_name, 0.0)
            
            if req > 500.0:
                tracker.apply_filter(f"Water requirement ({req}mm) too high for rainfed farm")
            elif req > 300.0:
                tracker.apply_multiplier(0.80, f"Water-intensive crop penalty applied for rainfed farm")
