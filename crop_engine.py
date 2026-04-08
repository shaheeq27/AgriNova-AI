import pandas as pd

data = pd.read_csv("crop_dataset.csv")


def recommend_crop(temp, rain):

    crops = []

    for _, row in data.iterrows():

        if row["rain_min"] <= rain <= row["rain_max"] and \
           row["temp_min"] <= temp <= row["temp_max"]:

            crops.append(row["crop"])

    return crops