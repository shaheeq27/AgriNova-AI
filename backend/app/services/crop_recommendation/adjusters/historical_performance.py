"""
AgriNova AI — Historical Performance Adjuster.
"""
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker

class HistoricalPerformanceAdjuster:
    """
    Adjusts scores based on the farm's historical yield success and momentum.
    """

    def apply(self, trackers: list[AdjustmentTracker], context: RecommendationContext):
        if not context.farm_performance:
            return

        yield_trends = {
            t.crop_name.lower(): t for t in context.farm_performance.yield_trends
        }
        perf_insights = {}
        for p in context.farm_performance.crop_performance:
            c_name = p.crop_name.lower()
            if c_name not in perf_insights:
                perf_insights[c_name] = {"crops_observed": 0, "harvested_count": 0}
            perf_insights[c_name]["crops_observed"] += p.crops_observed
            perf_insights[c_name]["harvested_count"] += p.harvested_count

        for tracker in trackers:
            if tracker.is_filtered:
                continue
                
            crop_name = tracker.crop.crop_name.lower()
            
            # 1. Momentum Bonus/Penalty
            trend = yield_trends.get(crop_name)
            if trend and trend.confidence and trend.confidence > 0.0:
                if trend.trend_direction == "increasing":
                    multiplier = 1.0 + (0.10 * trend.confidence)
                    tracker.apply_multiplier(multiplier, f"Strong increasing yield trend on this farm")
                elif trend.trend_direction == "decreasing":
                    multiplier = 1.0 - (0.10 * trend.confidence)
                    tracker.apply_multiplier(multiplier, f"Decreasing yield trend on this farm")
                    
            # 2. Historical Success (Fallback to raw success rate for now)
            perf = perf_insights.get(crop_name)
            if perf and perf["crops_observed"] > 0:
                # Note: harvested_count simply means the crop was harvested, not necessarily a good yield.
                # True yield-quality success metric requires an external baseline comparison in future versions.
                success_rate = perf["harvested_count"] / perf["crops_observed"]
                # If farm historically fails often with this crop
                if success_rate < 0.5 and perf["crops_observed"] >= 2:
                    tracker.apply_multiplier(0.85, "Poor historical success rate on this farm")
                # If farm historically excels
                elif success_rate >= 0.8 and perf["crops_observed"] >= 2:
                    tracker.apply_multiplier(1.05, "Proven historical success on this farm")
