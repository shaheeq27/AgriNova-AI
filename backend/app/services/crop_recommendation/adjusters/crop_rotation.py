"""
AgriNova AI — Crop Rotation Adjuster.
"""
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
from app.schemas.crop_v6_domain import BiologicalRisk, RiskLevel

class CropRotationAdjuster:
    """
    Evaluates biological risks based on crop rotation principles.
    """

    def apply(self, trackers: list[AdjustmentTracker], context: RecommendationContext):
        prev_crop = context.previous_crop
        if not prev_crop:
            return

        # Attempt to find the family of the previous crop from candidates
        # to avoid querying the database if not explicitly provided
        prev_family = context.previous_crop_family
        if not prev_family:
            for t in trackers:
                if t.crop.crop_name.lower() == prev_crop.lower() and t.crop.botanical_family:
                    prev_family = t.crop.botanical_family
                    break

        for tracker in trackers:
            if tracker.is_filtered:
                continue

            # 1. Same-crop penalty (e.g. Rice after Rice).
            if tracker.crop.crop_name.lower() == prev_crop.lower():
                risk = BiologicalRisk(
                    level=RiskLevel.HIGH,
                    factors=[f"Repeated crop planting ({prev_crop}) increases pathogen buildup and depletes specific soil nutrients."],
                    explanation=f"Planting {tracker.crop.crop_name} immediately after {prev_crop} poses a high biological risk."
                )
                tracker.biological_risks.append(risk)
                continue

            candidate_family = tracker.crop.botanical_family
            if not candidate_family or not prev_family:
                continue

            # 2. Same family penalty (e.g. Tomato after Potato)
            if candidate_family.lower() == prev_family.lower():
                risk = BiologicalRisk(
                    level=RiskLevel.MEDIUM,
                    factors=[f"Same-family rotation ({prev_family}) risks shared disease susceptibility."],
                    explanation=f"Planting a {candidate_family} crop after another {prev_family} poses a medium biological risk."
                )
                tracker.biological_risks.append(risk)
                continue

            # 3. Beneficial rotation: Cereals following Legumes
            if prev_family.lower() == "leguminosae" and candidate_family.lower() == "poaceae":
                tracker.positive_factors.append(
                    "Beneficial rotation: Cereal crop following a nitrogen-fixing Legume predecessor."
                )
