"""
AgriNova AI — Crop Recommendation Service.

Loads the trained ML model and provides explainable crop recommendations.
Falls back to rule-based matching from Knowledge Base if model is unavailable.
"""

import os
from typing import Any

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.schemas.historical_analysis import HistoricalInsightsContext

from app.models.knowledge import CropProfile

# ── Model Singleton ──
_model_bundle: dict | None = None
_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "ml", "models", "crop_recommender.joblib"
)


def _load_model() -> dict | None:
    """Load the trained model bundle (lazy singleton)."""
    global _model_bundle
    if _model_bundle is not None:
        return _model_bundle

    if not os.path.exists(_MODEL_PATH):
        return None

    try:
        import joblib
        _model_bundle = joblib.load(_MODEL_PATH)
        return _model_bundle
    except Exception:
        return None


async def recommend_crops(
    db: AsyncSession,
    temperature: float,
    humidity: float,
    rainfall: float,
    soil_type: str,
    n: float = 50,
    p: float = 35,
    k: float = 35,
    ph: float = 6.5,
    top_k: int = 5,
    historical_insights: HistoricalInsightsContext | None = None
) -> list[dict[str, Any]]:
    """Get top-K crop recommendations with explainable reasoning.

    Tries ML model first, falls back to Knowledge Base rule matching.

    Returns:
        List of dicts with: crop_name, confidence, explanation, growing_season, ideal_conditions
    """
    bundle = _load_model()

    if bundle is not None:
        return _recommend_ml(bundle, temperature, humidity, rainfall, soil_type, n, p, k, ph, top_k)

    # Fallback: rule-based from KB
    return await _recommend_rules(db, temperature, humidity, rainfall, soil_type, top_k)


def _recommend_ml(
    bundle: dict,
    temperature: float,
    humidity: float,
    rainfall: float,
    soil_type: str,
    n: float,
    p: float,
    k: float,
    ph: float,
    top_k: int,
) -> list[dict]:
    """ML-based recommendation using trained RandomForest."""
    model = bundle["model"]
    le = bundle["label_encoder"]
    feature_cols = bundle["feature_columns"]
    soil_types = bundle["soil_types"]
    numeric_features = bundle["numeric_features"]

    # Build feature vector
    numeric_vals = [temperature, humidity, rainfall, n, p, k, ph]
    soil_encoded = [1 if f"soil_{soil_type}" == col else 0 for col in feature_cols if col.startswith("soil_")]
    features = np.array(numeric_vals + soil_encoded).reshape(1, -1)

    # Get probabilities
    probas = model.predict_proba(features)[0]
    top_indices = np.argsort(probas)[::-1][:top_k]

    results = []
    for idx in top_indices:
        crop_name = le.inverse_transform([idx])[0]
        confidence = round(float(probas[idx]), 4)

        if confidence < 0.01:
            continue

        explanation = _build_explanation(
            crop_name, confidence, temperature, humidity, rainfall, soil_type, n, p, k, ph
        )

        results.append({
            "crop_name": crop_name,
            "confidence": confidence,
            "explanation": explanation,
            "model_version": "v1.0-rf",
        })

    return results


def _build_explanation(
    crop: str,
    confidence: float,
    temp: float,
    humidity: float,
    rainfall: float,
    soil: str,
    n: float,
    p: float,
    k: float,
    ph: float,
) -> str:
    """Generate a human-readable explanation for the recommendation."""
    reasons = []

    if temp > 25:
        reasons.append(f"warm climate ({temp:.0f}°C)")
    elif temp < 15:
        reasons.append(f"cool climate ({temp:.0f}°C)")
    else:
        reasons.append(f"moderate temperature ({temp:.0f}°C)")

    if humidity > 70:
        reasons.append("high humidity")
    elif humidity < 40:
        reasons.append("low humidity")

    if rainfall > 150:
        reasons.append("high rainfall region")
    elif rainfall < 50:
        reasons.append("low rainfall region")

    reasons.append(f"{soil.lower()} soil")

    if n > 60:
        reasons.append("nitrogen-rich soil")
    if p > 50:
        reasons.append("phosphorus-rich soil")
    if k > 50:
        reasons.append("potassium-rich soil")

    reason_str = ", ".join(reasons[:4])
    pct = confidence * 100

    return (
        f"{crop} is recommended with {pct:.0f}% confidence. "
        f"Your conditions ({reason_str}) align well with {crop}'s growth requirements."
    )


async def _recommend_rules(
    db: AsyncSession,
    temperature: float,
    humidity: float,
    rainfall: float,
    soil_type: str,
    top_k: int,
) -> list[dict]:
    """Rule-based fallback using Knowledge Base crop profiles."""
    result = await db.execute(select(CropProfile))
    profiles = result.scalars().all()

    scored = []
    for p in profiles:
        score = 0.0
        total = 4.0

        # Temperature match
        if p.temp_min <= temperature <= p.temp_max:
            score += 1.0
        else:
            dist = min(abs(temperature - p.temp_min), abs(temperature - p.temp_max))
            score += max(0, 1 - dist / 10)

        # Humidity match
        if p.humidity_min <= humidity <= p.humidity_max:
            score += 1.0
        else:
            dist = min(abs(humidity - p.humidity_min), abs(humidity - p.humidity_max))
            score += max(0, 1 - dist / 20)

        # Rainfall match
        if p.rain_min <= rainfall <= p.rain_max:
            score += 1.0
        else:
            dist = min(abs(rainfall - p.rain_min), abs(rainfall - p.rain_max))
            score += max(0, 1 - dist / 50)

        # Soil match
        if soil_type.lower() in p.ideal_soil_types.lower():
            score += 1.0

        confidence = round(score / total, 4)
        scored.append({
            "crop_name": p.crop_name,
            "confidence": confidence,
            "explanation": (
                f"{p.crop_name} matches your conditions with {confidence * 100:.0f}% fit. "
                f"Ideal range: {p.temp_min}-{p.temp_max}°C, {p.rain_min}-{p.rain_max}mm rainfall, "
                f"{p.ideal_soil_types} soil."
            ),
            "model_version": "v1.0-rules",
        })

    scored.sort(key=lambda x: x["confidence"], reverse=True)
    return scored[:top_k]
