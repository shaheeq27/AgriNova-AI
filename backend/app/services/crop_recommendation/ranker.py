"""
AgriNova AI — Deterministic Recommendation Ranker.
"""
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
from app.schemas.crop_v6_domain import RiskLevel, EvidenceStrength

class RecommendationRanker:
    """
    Ranks tracked crop candidates based on a multi-objective deterministic algorithm.
    """

    @staticmethod
    def _get_risk_value(tracker: AdjustmentTracker) -> int:
        """Extracts the maximum risk severity."""
        if not tracker.biological_risks:
            return 0

        mapping = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3
        }
        return max(mapping.get(r.level, 0) for r in tracker.biological_risks)

    @staticmethod
    def _get_evidence_value(tracker: AdjustmentTracker) -> int:
        """Extracts historical evidence strength."""
        if not tracker.historical_evidence:
            return 0

        mapping = {
            EvidenceStrength.NONE: 0,
            EvidenceStrength.INSUFFICIENT: 0,
            EvidenceStrength.LIMITED: 1,
            EvidenceStrength.STRONG: 2
        }
        return mapping.get(tracker.historical_evidence.level, 0)

    @staticmethod
    def sort_key(tracker: AdjustmentTracker):
        """
        Ranking lexicographical ordering:
        1. Agronomic suitability (descending)
        2. Biological risk severity (ascending) -> lower is better
        3. Historical evidence strength (descending)
        4. Crop name (ascending tie-breaker)

        Eligibility is handled externally (ineligible candidates are filtered out).
        """
        suitability = tracker.base_score
        risk_val = RecommendationRanker._get_risk_value(tracker)
        evidence_val = RecommendationRanker._get_evidence_value(tracker)
        crop_name = tracker.crop.crop_name

        return (-suitability, risk_val, -evidence_val, crop_name)

    @staticmethod
    def rank(trackers: list[AdjustmentTracker]) -> list[AdjustmentTracker]:
        """Filters out ineligible crops and sorts the remainder."""
        eligible = [t for t in trackers if not t.is_filtered]
        eligible.sort(key=RecommendationRanker.sort_key)
        return eligible
