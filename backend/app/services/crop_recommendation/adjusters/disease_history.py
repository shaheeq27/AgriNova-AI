"""
AgriNova AI — Disease History Adjuster.
"""
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
from app.schemas.crop_v6_domain import BiologicalRisk, RiskLevel

class DiseaseHistoryAdjuster:
    """
    Evaluates biological risk based on historical disease patterns on the farm.
    """

    def apply(self, trackers: list[AdjustmentTracker], context: RecommendationContext):
        if not context.disease_history:
            return

        for tracker in trackers:
            if tracker.is_filtered:
                continue

            crop_name = tracker.crop.crop_name.lower()

            # Find relevant disease insights
            for insight in context.disease_history:
                affected_crop = insight.affected_crop.lower()

                # Match only if it's the exact same crop.
                # Family-level disease propagation is explicitly omitted because the system
                # currently lacks a strict pathogen-host relationship knowledge graph.
                if crop_name == affected_crop and insight.occurrence_count > 1:
                    sev = (insight.common_severity or "").lower()

                    risk_level = RiskLevel.MEDIUM
                    if sev == "critical":
                        risk_level = RiskLevel.HIGH

                    risk = BiologicalRisk(
                        level=risk_level,
                        factors=[f"Historical presence of {insight.disease_name} (Severity: {sev.title()}). Exact crop match ({insight.affected_crop})."],
                        explanation=f"Farm history indicates recurring {insight.disease_name}, posing a {risk_level.value} biological risk.",
                        is_farm_history_based=True
                    )
                    tracker.biological_risks.append(risk)
