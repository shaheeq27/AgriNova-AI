"""
AgriNova AI — Knowledge Base seed data script.

Populates the Knowledge Base tables from the existing crop_dataset.csv
and expanded agronomic reference data.

Usage:
    cd backend && python -m data.seed_knowledge
"""

import asyncio
import csv
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import async_session_factory, init_db
from app.models.knowledge import (
    CropProfile,
    DiseaseLibrary,
    FertilizerLibrary,
    GrowthStage,
    IrrigationGuideline,
)


# ── Growth stages (generic templates per crop type) ──
GENERIC_STAGES = [
    {"stage_name": "Germination", "stage_order": 1, "duration_days": 10, "description": "Seed sprouting and root establishment", "key_activities": "Ensure adequate moisture, monitor temperature"},
    {"stage_name": "Seedling", "stage_order": 2, "duration_days": 15, "description": "Early growth and leaf development", "key_activities": "Thin seedlings, first weeding, light irrigation"},
    {"stage_name": "Vegetative", "stage_order": 3, "duration_days": 30, "description": "Rapid growth of stems and leaves", "key_activities": "Fertilizer application, pest monitoring, regular irrigation"},
    {"stage_name": "Flowering", "stage_order": 4, "duration_days": 20, "description": "Flower development and pollination", "key_activities": "Reduce nitrogen, ensure pollination, watch for disease"},
    {"stage_name": "Fruiting", "stage_order": 5, "duration_days": 25, "description": "Fruit/grain development and filling", "key_activities": "Maintain irrigation, potassium application, pest control"},
    {"stage_name": "Maturity", "stage_order": 6, "duration_days": 15, "description": "Crop reaches harvest readiness", "key_activities": "Reduce irrigation, check moisture content, plan harvest"},
]


# ── Common diseases ──
DISEASES = [
    {
        "disease_name": "Leaf Blight",
        "affected_crops": "Rice, Wheat, Maize, Barley",
        "symptoms": "Brown lesions on leaves starting from tips, wilting, yellowing of leaf margins",
        "treatment": "Apply mancozeb or copper-based fungicide. Remove infected leaves. Improve air circulation.",
        "prevention": "Use disease-resistant varieties. Avoid overhead irrigation. Maintain proper spacing.",
        "severity": "high",
    },
    {
        "disease_name": "Powdery Mildew",
        "affected_crops": "Wheat, Peas, Mustard, Okra, Chili",
        "symptoms": "White powdery coating on leaves and stems, distorted growth, premature leaf drop",
        "treatment": "Apply sulfur-based fungicide or neem oil spray. Remove heavily infected parts.",
        "prevention": "Ensure good air circulation. Avoid excessive nitrogen fertilizer. Water at base of plants.",
        "severity": "medium",
    },
    {
        "disease_name": "Root Rot",
        "affected_crops": "Soybean, Groundnut, Cotton, Pulses",
        "symptoms": "Yellowing and wilting of plants, brown/black roots, stunted growth, plant collapse",
        "treatment": "Apply trichoderma-based biocontrol. Improve drainage. Remove infected plants.",
        "prevention": "Avoid waterlogging. Rotate crops. Use treated seeds. Maintain soil pH 6-7.",
        "severity": "high",
    },
    {
        "disease_name": "Bacterial Wilt",
        "affected_crops": "Tomato, Potato, Brinjal, Chili, Ginger",
        "symptoms": "Sudden wilting of entire plant, brown vascular tissue when stem is cut, no yellowing before wilt",
        "treatment": "No chemical cure. Remove and destroy infected plants. Solarize soil.",
        "prevention": "Use resistant varieties. Practice crop rotation (3-4 years). Avoid injured transplants.",
        "severity": "critical",
    },
    {
        "disease_name": "Downy Mildew",
        "affected_crops": "Millet, Maize, Sunflower, Onion, Spinach",
        "symptoms": "Yellow patches on upper leaf surface, gray-white fluffy growth on undersides, stunted plants",
        "treatment": "Apply metalaxyl-based fungicide. Improve ventilation. Remove infected debris.",
        "prevention": "Use treated seeds. Avoid dense planting. Ensure good field drainage.",
        "severity": "medium",
    },
    {
        "disease_name": "Rust",
        "affected_crops": "Wheat, Barley, Coffee, Sugarcane, Soybean",
        "symptoms": "Orange-brown pustules on leaves and stems, premature defoliation, reduced grain filling",
        "treatment": "Apply propiconazole or tebuconazole fungicide. Remove volunteer plants.",
        "prevention": "Plant resistant varieties. Early sowing. Destroy crop residues.",
        "severity": "high",
    },
    {
        "disease_name": "Anthracnose",
        "affected_crops": "Mango, Banana, Chili, Onion, Turmeric",
        "symptoms": "Dark sunken lesions on fruits, leaves, and stems. Dieback of twigs. Fruit rot.",
        "treatment": "Apply carbendazim or copper oxychloride. Prune infected parts. Hot water seed treatment.",
        "prevention": "Use disease-free planting material. Maintain field hygiene. Avoid overhead irrigation.",
        "severity": "medium",
    },
    {
        "disease_name": "Late Blight",
        "affected_crops": "Potato, Tomato",
        "symptoms": "Water-soaked dark lesions on leaves, white mold on undersides, rapid browning, tuber rot",
        "treatment": "Apply mancozeb + metalaxyl. Remove infected plants immediately. Harvest early if severe.",
        "prevention": "Use certified disease-free seed. Plant resistant varieties. Avoid evening irrigation.",
        "severity": "critical",
    },
]


# ── Irrigation water requirements by soil type (mm per stage) ──
IRRIGATION_BY_SOIL = {
    "Clay": {"water_mm": 35, "frequency": "Every 5-7 days", "method": "Furrow or drip"},
    "Loamy": {"water_mm": 30, "frequency": "Every 4-5 days", "method": "Drip or sprinkler"},
    "Sandy": {"water_mm": 25, "frequency": "Every 2-3 days", "method": "Drip irrigation"},
    "Black": {"water_mm": 40, "frequency": "Every 6-8 days", "method": "Furrow irrigation"},
    "Red": {"water_mm": 28, "frequency": "Every 3-4 days", "method": "Drip or sprinkler"},
    "Alluvial": {"water_mm": 32, "frequency": "Every 4-5 days", "method": "Any method"},
}


async def seed_all():
    """Populate all Knowledge Base tables."""
    await init_db()

    async with async_session_factory() as session:
        # ── 1. Seed Crop Profiles from CSV ──
        csv_path = Path(__file__).resolve().parent.parent.parent / "data" / "crop_dataset.csv"
        if not csv_path.exists():
            print(f"⚠️  CSV not found at {csv_path}, skipping crop profiles")
        else:
            with open(csv_path, newline="") as f:
                reader = csv.DictReader(f)
                crop_count = 0
                for row in reader:
                    profile = CropProfile(
                        crop_name=row["crop_name"].strip(),
                        temp_min=float(row["temp_min"]),
                        temp_max=float(row["temp_max"]),
                        rain_min=float(row["rain_min"]),
                        rain_max=float(row["rain_max"]),
                        humidity_min=float(row["humidity_min"]),
                        humidity_max=float(row["humidity_max"]),
                        ideal_soil_types=row["soil_type"].strip(),
                        growing_season=row["season"].strip(),
                        description=f"Optimal conditions for growing {row['crop_name'].strip()}",
                    )
                    session.add(profile)
                    crop_count += 1

                    # Seed growth stages for this crop
                    for stage in GENERIC_STAGES:
                        session.add(GrowthStage(
                            crop_name=row["crop_name"].strip(),
                            **stage,
                        ))

                    # Seed fertilizer guidelines from CSV data
                    if row.get("fertilizer"):
                        session.add(FertilizerLibrary(
                            crop_name=row["crop_name"].strip(),
                            stage_name="Vegetative",
                            fertilizer_type=row["fertilizer"].strip(),
                            quantity_per_acre=float(row.get("fertilizer_per_acre", 50)),
                            unit="kg",
                            timing=row.get("fertilizer_time", "As per schedule").strip(),
                            application_method="Broadcasting or side dressing",
                        ))

                    # Seed irrigation guidelines per soil type
                    soil = row["soil_type"].strip()
                    if soil in IRRIGATION_BY_SOIL:
                        info = IRRIGATION_BY_SOIL[soil]
                        for stage in ["Germination", "Vegetative", "Flowering", "Fruiting"]:
                            session.add(IrrigationGuideline(
                                crop_name=row["crop_name"].strip(),
                                stage_name=stage,
                                soil_type=soil,
                                water_requirement_mm=info["water_mm"],
                                frequency=info["frequency"],
                                method=info["method"],
                            ))

                print(f"✅ Seeded {crop_count} crop profiles with stages, fertilizer & irrigation guidelines")

        # ── 2. Seed Disease Library ──
        for disease in DISEASES:
            session.add(DiseaseLibrary(**disease))
        print(f"✅ Seeded {len(DISEASES)} disease entries")

        await session.commit()
        print("\n🌱 Knowledge Base seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_all())
