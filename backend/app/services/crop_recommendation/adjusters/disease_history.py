"""
AgriNova AI — Disease History Adjuster.
"""
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker

class DiseaseHistoryAdjuster:
    """
    Penalizes crops based on historical disease patterns on the farm.
    """

    def apply(self, trackers: list[AdjustmentTracker], context: RecommendationContext):
        if not context.disease_history:
            return

        for tracker in trackers:
            if tracker.is_filtered:
                continue
                
            crop_name = tracker.crop.crop_name
            
            # Find relevant disease insights
            for insight in context.disease_history:
                # Disease matching is performed exactly at the crop level
                # using the singular affected_crop field.
                is_affected = (crop_name.lower() == insight.affected_crop.lower())
                
                if is_affected and insight.occurrence_count > 1:
                    sev = (insight.common_severity or "").lower()
                    if sev == "critical":
                        tracker.apply_multiplier(0.80, f"Critical historical disease risk ({insight.disease_name})")
                    elif sev == "high":
                        tracker.apply_multiplier(0.90, f"High historical disease risk ({insight.disease_name})")
