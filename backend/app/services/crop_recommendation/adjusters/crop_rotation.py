"""
AgriNova AI — Crop Rotation Adjuster.
"""
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker

# Botanical family mapping for all 30 crops in the current Knowledge Base.
# Each entry is verified against the crop_dataset.csv crop list.
# Do not add entries for crops that are not present in the KB.
CROP_FAMILIES = {
    # Poaceae (Grasses/Cereals) — Heavy nitrogen feeders
    "Wheat": "Poaceae",
    "Rice": "Poaceae",
    "Maize": "Poaceae",
    "Barley": "Poaceae",
    "Millet": "Poaceae",
    "Sugarcane": "Poaceae",

    # Leguminosae (Legumes) — Nitrogen fixers
    "Soybean": "Leguminosae",
    "Groundnut": "Leguminosae",
    "Peas": "Leguminosae",
    "Pulses": "Leguminosae",

    # Solanaceae (Nightshades)
    "Tomato": "Solanaceae",
    "Potato": "Solanaceae",
    "Brinjal": "Solanaceae",
    "Chili": "Solanaceae",

    # Malvaceae
    "Cotton": "Malvaceae",
    "Okra": "Malvaceae",

    # Brassicaceae
    "Mustard": "Brassicaceae",
    "Cabbage": "Brassicaceae",

    # Amaryllidaceae (Alliums)
    "Onion": "Amaryllidaceae",
    "Garlic": "Amaryllidaceae",

    # Zingiberaceae (Gingers)
    "Turmeric": "Zingiberaceae",
    "Ginger": "Zingiberaceae",

    # Asteraceae (Composites)
    "Sunflower": "Asteraceae",

    # Pedaliaceae
    "Sesame": "Pedaliaceae",

    # Theaceae
    "Tea": "Theaceae",

    # Rubiaceae
    "Coffee": "Rubiaceae",

    # Musaceae
    "Banana": "Musaceae",

    # Anacardiaceae
    "Mango": "Anacardiaceae",

    # Apiaceae
    "Carrot": "Apiaceae",

    # Amaranthaceae
    "Spinach": "Amaranthaceae",
}


class CropRotationAdjuster:
    """
    Adjusts scores based on crop rotation principles.
    Penalizes same-family planting, rewards beneficial rotations (e.g., following a Legume).
    """

    def apply(self, trackers: list[AdjustmentTracker], context: RecommendationContext):
        prev_crop = context.previous_crop
        if not prev_crop:
            return

        prev_family = context.previous_crop_family
        if not prev_family:
            prev_family = CROP_FAMILIES.get(prev_crop)

        for tracker in trackers:
            if tracker.is_filtered:
                continue

            # 1. Same-crop penalty (e.g. Rice after Rice).
            #    This does NOT require family information.
            if tracker.crop.crop_name.lower() == prev_crop.lower():
                tracker.apply_multiplier(0.85, f"Repeated crop planting penalty ({prev_crop})")
                continue

            # Family-level adjustments require both prev and candidate families.
            candidate_family = CROP_FAMILIES.get(tracker.crop.crop_name)
            if not candidate_family or not prev_family:
                continue

            # 2. Same family penalty (e.g. Tomato after Potato)
            if candidate_family == prev_family:
                tracker.apply_multiplier(0.90, f"Same-family rotation penalty ({prev_family})")
                continue

            # 3. Beneficial rotation: Cereals following Legumes
            if prev_family == "Leguminosae" and candidate_family == "Poaceae":
                tracker.apply_multiplier(1.10, "Beneficial rotation bonus (Nitrogen-fixing Legume predecessor)")
