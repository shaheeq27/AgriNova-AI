"""
AgriNova AI — Season Filter.
"""
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
from app.schemas.crop_v6_domain import HardConstraint, EligibilityStatus

class SeasonFilter:
    """
    Filters candidates based on season compatibility.
    Does not modify the base score.
    """

    def apply(self, trackers: list[AdjustmentTracker], context: RecommendationContext):
        """
        Evaluates season constraint:
        - No target season is supplied
        - Target season matches growing season
        - Growing season is "All"
        """
        if not context.season:
            for tracker in trackers:
                tracker.eligibility_constraints.append(
                    HardConstraint(status=EligibilityStatus.ELIGIBLE, reason="No specific season requested.")
                )
            return

        target_season = context.season.strip().lower()

        # Map frontend values to canonical DB values
        season_map = {
            "zaid": "summer",
            "annual": "all"
        }
        target_season = season_map.get(target_season, target_season)

        for tracker in trackers:
            crop_season = (tracker.crop.growing_season or "").strip().lower()
            if crop_season == target_season or crop_season == "all":
                tracker.eligibility_constraints.append(
                    HardConstraint(status=EligibilityStatus.ELIGIBLE, reason=f"Crop season ({crop_season}) is compatible with target season ({target_season}).")
                )
            else:
                reason = f"Crop season ({crop_season}) does not match target season ({target_season})."
                tracker.eligibility_constraints.append(
                    HardConstraint(status=EligibilityStatus.INELIGIBLE, reason=reason)
                )
                tracker.apply_filter(reason)
