"""
AgriNova AI — V6 Crop Recommendation Interfaces.
"""

from abc import ABC, abstractmethod

from app.models.knowledge import CropProfile
from app.services.crop_recommendation.context import RecommendationContext

class RecommendationScorer(ABC):
    """
    Abstract interface for scoring crop candidates.
    Allows seamlessly switching between deterministic (rules) and probabilistic (ML) scoring.
    """

    @abstractmethod
    async def score_candidates(
        self,
        candidates: list[CropProfile],
        context: RecommendationContext
    ) -> dict[str, tuple[float, float, str, list[str], list[str]]]:
        """
        Score a list of crop profiles based on the provided context.

        Args:
            candidates: List of CropProfiles to score.
            context: Canonical RecommendationContext.

        Returns:
            A dictionary mapping crop_name to a tuple of:
            (base_score, evidence_coverage_ratio, base_explanation, list_of_positive_factors, list_of_negative_factors)
        """
        pass
