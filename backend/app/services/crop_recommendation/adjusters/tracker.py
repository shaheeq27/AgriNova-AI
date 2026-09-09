"""
AgriNova AI — Adjustment Tracker.
"""
from dataclasses import dataclass, field
from app.models.knowledge import CropProfile
from app.schemas.crop_v6 import ExplanationPayload

@dataclass
class AdjustmentTracker:
    """Tracks score adjustments and explanations for a single candidate."""
    crop: CropProfile
    base_score: float
    current_score: float
    
    positive_factors: list[str] = field(default_factory=list)
    negative_factors: list[str] = field(default_factory=list)
    constraints_applied: list[str] = field(default_factory=list)
    is_filtered: bool = False
    
    def apply_multiplier(self, multiplier: float, reason: str):
        """Applies a multiplicative adjustment and tracks the reason.

        Every applied multiplier is recorded in the explanation regardless
        of the numerical delta, so that low-scoring crops still receive
        full explanation traceability.
        """
        if self.is_filtered:
            return

        self.current_score *= multiplier
        self.current_score = min(1.0, max(0.0, self.current_score))
        self.current_score = round(self.current_score, 4)

        if multiplier > 1.0:
            self.positive_factors.append(reason)
        elif multiplier < 1.0:
            self.negative_factors.append(reason)

    def apply_filter(self, reason: str):
        """Applies a hard constraint that drops the crop."""
        self.current_score = 0.0
        self.is_filtered = True
        self.constraints_applied.append(reason)

    def to_explanation_payload(self) -> ExplanationPayload:
        """Converts tracked data to the standard explanation payload."""
        return ExplanationPayload(
            base_explanation=f"Base environmental suitability: {self.base_score:.2f}",
            positive_factors=self.positive_factors.copy(),
            negative_factors=self.negative_factors.copy(),
            constraints_applied=self.constraints_applied.copy()
        )
