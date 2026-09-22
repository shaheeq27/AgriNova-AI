"""
AgriNova AI — Historical Performance Adjuster.
"""
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
from app.schemas.crop_v6_domain import HistoricalEvidence, EvidenceStrength

class HistoricalPerformanceAdjuster:
    """
    Evaluates historical yield success and momentum into HistoricalEvidence.
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

            trend = yield_trends.get(crop_name)
            perf = perf_insights.get(crop_name)

            obs_count = perf["crops_observed"] if perf else 0
            success_count = perf["harvested_count"] if perf else 0

            if obs_count == 0 and not trend:
                tracker.historical_evidence = HistoricalEvidence(
                    level=EvidenceStrength.NONE,
                    explanation="No historical data available for this crop on this farm."
                )
                continue

            level = EvidenceStrength.INSUFFICIENT
            factors = []

            if obs_count >= 2:
                success_rate = success_count / obs_count
                if success_rate >= 0.8:
                    level = EvidenceStrength.STRONG
                    factors.append("Proven high historical success rate on this farm.")
                elif success_rate < 0.5:
                    # Poor success rate represents lack of positive evidence
                    level = EvidenceStrength.NONE
                    factors.append("Poor historical success rate on this farm.")
                else:
                    level = EvidenceStrength.LIMITED
                    factors.append("Mixed historical success rate on this farm.")
            elif obs_count == 1:
                factors.append("Insufficient historical observations to establish reliability.")

            trend_dir = trend.trend_direction if trend else None
            if trend and trend.confidence and trend.confidence > 0.0:
                if trend_dir == "increasing":
                    factors.append(f"Strong increasing yield trend.")
                    if level == EvidenceStrength.LIMITED:
                        level = EvidenceStrength.STRONG
                elif trend_dir == "decreasing":
                    factors.append(f"Decreasing yield trend.")
                    if level == EvidenceStrength.STRONG:
                        level = EvidenceStrength.LIMITED

            tracker.historical_evidence = HistoricalEvidence(
                level=level,
                observations=obs_count,
                successful_observations=success_count,
                trend=trend_dir,
                supporting_factors=factors,
                explanation=f"Farm history provides {level.value} positive evidence based on {obs_count} past cycles."
            )
