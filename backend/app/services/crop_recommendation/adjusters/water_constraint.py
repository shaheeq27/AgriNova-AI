"""
AgriNova AI — Water Constraint Adjuster.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
from app.schemas.crop_v6_domain import HardConstraint, EligibilityStatus

class WaterConstraintAdjuster:
    """
    Adjusts or filters crops based on farm water availability.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def apply(self, trackers: list[AdjustmentTracker], context: RecommendationContext):
        if not context.water_source:
            # Unavailable information -> DO NOT assume irrigation -> DO NOT assume rainfed -> do not apply a water constraint
            return

        water_source = context.water_source.strip().lower()

        if water_source in ["none", "rainfed"]:
            # Explicit rainfed condition -> water constraint may apply
            pass
        elif water_source in ["canal", "borewell", "drip", "sprinkler"]:
            # Explicit irrigation -> no rainfed constraint
            return
        else:
            # Unknown/unrecognized water source -> do not invent its meaning -> do not apply a rainfed constraint
            return

        for tracker in trackers:
            if tracker.is_filtered:
                continue

            req = tracker.crop.water_requirement_mm

            if req is None:
                # No crop-specific requirement exists -> unavailable constraint
                continue

            rainfall = context.rainfall

            if rainfall is not None:
                if req > rainfall:
                    reason = f"Crop requires {req}mm water, but only {rainfall}mm rainfall expected for this rainfed farm."
                    constraint = HardConstraint(status=EligibilityStatus.INELIGIBLE, reason=reason)
                    tracker.eligibility_constraints.append(constraint)
                    tracker.apply_filter(reason)
                else:
                    reason = f"Expected rainfall ({rainfall}mm) meets crop requirement ({req}mm)."
                    constraint = HardConstraint(status=EligibilityStatus.ELIGIBLE, reason=reason)
                    tracker.eligibility_constraints.append(constraint)
