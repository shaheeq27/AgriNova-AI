"""
AgriNova AI — Adjustment Tracker.
"""
from dataclasses import dataclass, field
from app.models.knowledge import CropProfile
from app.schemas.crop_v6 import ExplanationPayload
from app.schemas.crop_v6_domain import HardConstraint, BiologicalRisk, HistoricalEvidence, EvidenceStrength

@dataclass
class AdjustmentTracker:
    """Tracks domain evaluations and explanations for a single candidate."""
    crop: CropProfile
    base_score: float
    base_explanation: str = ""
    evidence_coverage_ratio: float = 1.0

    positive_factors: list[str] = field(default_factory=list)
    negative_factors: list[str] = field(default_factory=list)
    constraints_applied: list[str] = field(default_factory=list)
    is_filtered: bool = False

    # New C.7 domain structures
    eligibility_constraints: list["HardConstraint"] = field(default_factory=list)
    biological_risks: list["BiologicalRisk"] = field(default_factory=list)
    historical_evidence: "HistoricalEvidence | None" = None

    def apply_filter(self, reason: str):
        """Applies a hard constraint that drops the crop."""
        self.is_filtered = True
        self.constraints_applied.append(reason)

    def to_explanation_payload(self) -> ExplanationPayload:
        """Converts tracked data to the standard explanation payload."""
        explanation_text = self.base_explanation or f"Base environmental suitability: {self.base_score:.2f}"

        return ExplanationPayload(
            base_explanation=explanation_text,
            positive_factors=self.positive_factors.copy(),
            negative_factors=self.negative_factors.copy(),
            constraints_applied=self.constraints_applied.copy(),
            evidence_coverage_ratio=self.evidence_coverage_ratio
        )
