import pickle
import numpy as np

model = pickle.load(open("model.pkl", "rb"))
le_soil = pickle.load(open("soil_encoder.pkl", "rb"))
le_season = pickle.load(open("season_encoder.pkl", "rb"))
le_crop = pickle.load(open("crop_encoder.pkl", "rb"))


def clean_input(value):
    return value.strip().lower()


def normalize_soil(soil):
    soil = clean_input(soil)

    if "loam" in soil:
        return "Loamy"
    elif "clay" in soil:
        return "Clay"
    elif "sand" in soil:
        return "Sandy"
    elif "black" in soil:
        return "Black"
    elif "red" in soil:
        return "Red"
    elif "alluvial" in soil:
        return "Alluvial"

    return None


def normalize_season(season):
    season = clean_input(season)

    if "kharif" in season:
        return "Kharif"
    elif "rabi" in season:
        return "Rabi"
    elif "summer" in season:
        return "Summer"

    return None


def predict_crop(temp, rain, humidity, soil, season):

    soil = normalize_soil(soil)
    season = normalize_season(season)

    if not soil or not season:
        return []

    try:
        soil_encoded = le_soil.transform([soil])[0]
        season_encoded = le_season.transform([season])[0]
    except:
        return []

    features = np.array([[temp, rain, humidity, soil_encoded, season_encoded]])

    # 🔥 Get probabilities
    probs = model.predict_proba(features)[0]

    # Get top 3 indices
    top_indices = probs.argsort()[-3:][::-1]

    results = []

    for idx in top_indices:
        crop_name = le_crop.inverse_transform([idx])[0]
        confidence = round(probs[idx] * 100, 2)

        results.append({
            "name": crop_name,
            "confidence": confidence
        })

    return results