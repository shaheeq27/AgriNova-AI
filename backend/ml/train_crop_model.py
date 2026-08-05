"""
AgriNova AI — ML Crop Recommendation Model Training.

Trains a RandomForest classifier on augmented crop data.
Features: temperature, humidity, rainfall, N, P, K, ph + one-hot soil_type
Target: crop_name
"""

import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Synthetic N/P/K/pH profiles per crop (realistic agronomic values)
CROP_NPK = {
    "Rice": {"N": 80, "P": 40, "K": 40, "ph": 6.0},
    "Wheat": {"N": 60, "P": 40, "K": 20, "ph": 6.5},
    "Maize": {"N": 80, "P": 40, "K": 20, "ph": 6.0},
    "Cotton": {"N": 60, "P": 30, "K": 30, "ph": 7.0},
    "Sugarcane": {"N": 100, "P": 50, "K": 50, "ph": 6.5},
    "Groundnut": {"N": 20, "P": 60, "K": 30, "ph": 6.2},
    "Soybean": {"N": 20, "P": 60, "K": 40, "ph": 6.5},
    "Tomato": {"N": 60, "P": 80, "K": 60, "ph": 6.2},
    "Potato": {"N": 80, "P": 80, "K": 80, "ph": 5.5},
    "Onion": {"N": 40, "P": 40, "K": 60, "ph": 6.5},
    "Banana": {"N": 100, "P": 40, "K": 100, "ph": 6.0},
    "Mango": {"N": 40, "P": 20, "K": 40, "ph": 6.0},
    "Coconut": {"N": 50, "P": 30, "K": 80, "ph": 6.0},
    "Tea": {"N": 60, "P": 20, "K": 20, "ph": 4.5},
    "Coffee": {"N": 40, "P": 20, "K": 30, "ph": 5.5},
    "Turmeric": {"N": 60, "P": 30, "K": 60, "ph": 6.0},
    "Ginger": {"N": 50, "P": 30, "K": 50, "ph": 5.5},
    "Pepper": {"N": 40, "P": 30, "K": 40, "ph": 6.0},
    "Chilli": {"N": 50, "P": 40, "K": 30, "ph": 6.5},
    "Brinjal": {"N": 50, "P": 40, "K": 40, "ph": 6.0},
    "Cabbage": {"N": 60, "P": 40, "K": 40, "ph": 6.5},
    "Carrot": {"N": 30, "P": 40, "K": 50, "ph": 6.3},
    "Cauliflower": {"N": 60, "P": 50, "K": 30, "ph": 6.5},
    "Cucumber": {"N": 40, "P": 40, "K": 40, "ph": 6.5},
    "Garlic": {"N": 30, "P": 30, "K": 50, "ph": 6.5},
    "Barley": {"N": 40, "P": 30, "K": 20, "ph": 7.0},
    "Mustard": {"N": 40, "P": 20, "K": 20, "ph": 7.0},
    "Sunflower": {"N": 50, "P": 40, "K": 30, "ph": 6.5},
    "Jute": {"N": 40, "P": 20, "K": 20, "ph": 6.5},
    "Lentil": {"N": 20, "P": 40, "K": 20, "ph": 6.5},
}

DEFAULT_NPK = {"N": 50, "P": 35, "K": 35, "ph": 6.5}

SOIL_TYPES = ["Clay", "Loamy", "Sandy", "Black", "Red", "Alluvial", "Laterite"]


def load_and_augment(csv_path: str, samples_per_crop: int = 150) -> pd.DataFrame:
    """Load CSV and augment with synthetic samples within valid ranges."""
    df = pd.read_csv(csv_path)
    rows = []

    for _, row in df.iterrows():
        crop = row["crop_name"]
        npk = CROP_NPK.get(crop, DEFAULT_NPK)

        for _ in range(samples_per_crop):
            temp = np.random.uniform(row["temp_min"], row["temp_max"])
            rain = np.random.uniform(row["rain_min"], row["rain_max"])
            hum = np.random.uniform(row["humidity_min"], row["humidity_max"])
            n = npk["N"] + np.random.normal(0, npk["N"] * 0.15)
            p = npk["P"] + np.random.normal(0, npk["P"] * 0.15)
            k = npk["K"] + np.random.normal(0, npk["K"] * 0.15)
            ph = npk["ph"] + np.random.normal(0, 0.3)

            # Parse soil types and pick one
            soils = [s.strip() for s in row["soil_type"].split("/")]
            soil = np.random.choice(soils)

            rows.append({
                "temperature": round(temp, 1),
                "humidity": round(hum, 1),
                "rainfall": round(rain, 1),
                "N": round(max(0, n), 1),
                "P": round(max(0, p), 1),
                "K": round(max(0, k), 1),
                "ph": round(np.clip(ph, 3.5, 9.0), 1),
                "soil_type": soil,
                "crop_name": crop,
            })

    return pd.DataFrame(rows)


def train():
    """Train and save the crop recommendation model."""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "crop_dataset.csv")
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(model_dir, exist_ok=True)

    print("🌱 AgriNova AI — Crop Recommendation Model Training")
    print("=" * 55)

    # 1. Load & augment
    print("\n📊 Loading and augmenting dataset...")
    df = load_and_augment(csv_path)
    print(f"   Generated {len(df)} samples from {df['crop_name'].nunique()} crops")

    # 2. Feature engineering
    numeric_features = ["temperature", "humidity", "rainfall", "N", "P", "K", "ph"]
    df_encoded = pd.get_dummies(df, columns=["soil_type"], prefix="soil")
    soil_cols = [c for c in df_encoded.columns if c.startswith("soil_")]
    feature_cols = numeric_features + soil_cols

    X = df_encoded[feature_cols].values
    le = LabelEncoder()
    y = le.fit_transform(df_encoded["crop_name"])

    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Train: {len(X_train)}, Test: {len(X_test)}")

    # 4. Train
    print("\n🤖 Training RandomForest (n_estimators=200)...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # 5. Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n📈 Test Accuracy: {accuracy:.4f} ({accuracy * 100:.1f}%)")
    print("\n📋 Per-class Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # 6. Save
    import joblib

    model_path = os.path.join(model_dir, "crop_recommender.joblib")
    joblib.dump({
        "model": model,
        "label_encoder": le,
        "feature_columns": feature_cols,
        "soil_types": SOIL_TYPES,
        "numeric_features": numeric_features,
    }, model_path)

    metadata = {
        "model_type": "RandomForestClassifier",
        "n_estimators": 200,
        "n_features": len(feature_cols),
        "n_classes": len(le.classes_),
        "classes": list(le.classes_),
        "feature_columns": feature_cols,
        "accuracy": round(accuracy, 4),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
    }
    with open(os.path.join(model_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✅ Model saved to {model_path}")
    print(f"✅ Metadata saved to {os.path.join(model_dir, 'metadata.json')}")
    print(f"\n🎯 Model predicts {len(le.classes_)} crops with {accuracy * 100:.1f}% accuracy")


if __name__ == "__main__":
    train()
