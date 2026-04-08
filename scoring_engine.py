import pandas as pd

CROP_DATA = pd.read_csv("data/crop_dataset.csv")


def load_crop_data():
    return CROP_DATA


def range_score(value, min_val, max_val, weight):

    range_width = max_val - min_val
    if range_width == 0:
        return weight

    if value < min_val:
        diff = min_val - value
    elif value > max_val:
        diff = value - max_val
    else:
        return weight

    penalty = diff / range_width

    score = weight * max(0, 1 - penalty)

    return score


def soil_score(user_soil, crop_soil):

    if user_soil.lower() == crop_soil.lower():
        return 15
    else:
        return 0


def season_score(user_season, crop_season):

    if crop_season.lower() == "all":
        return 10

    if user_season.lower() == crop_season.lower():
        return 10

    return 0


def calculate_score(crop, temp, rain, humidity, soil, season):

    temp_score = range_score(temp, crop["temp_min"], crop["temp_max"], 30)

    rain_score = range_score(rain, crop["rain_min"], crop["rain_max"], 30)

    humidity_score = range_score(
        humidity, crop["humidity_min"], crop["humidity_max"], 15
    )

    soil_match = soil_score(soil, crop["soil_type"])

    season_match = season_score(season, crop["season"])

    total_score = (
        temp_score +
        rain_score +
        humidity_score +
        soil_match +
        season_match
    )

    return round(total_score, 2)


def rank_crops(temp, rain, humidity, soil, season):

    crops_df = load_crop_data()

    results = []

    for _, crop in crops_df.iterrows():

        score = calculate_score(crop, temp, rain, humidity, soil, season)

        crop_data = {
    "name": crop["crop_name"],
    "score": score,
    "fertilizer": crop["fertilizer"],
    "fertilizer_time": crop["fertilizer_time"],
    "fertilizer_per_acre": crop["fertilizer_per_acre"]
}

        results.append(crop_data)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:3]