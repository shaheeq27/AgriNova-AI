import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
df = pd.read_csv("data/crop_dataset.csv")

# Encoders
le_soil = LabelEncoder()
le_season = LabelEncoder()
le_crop = LabelEncoder()

df["soil_type"] = le_soil.fit_transform(df["soil_type"])
df["season"] = le_season.fit_transform(df["season"])
df["crop_name"] = le_crop.fit_transform(df["crop_name"])

# Features (INPUT)
X = df[["temp_min", "rain_min", "humidity_min", "soil_type", "season"]]

# Target (OUTPUT)
y = df["crop_name"]

# Train model
model = RandomForestClassifier(n_estimators=200, max_depth=10)
model.fit(X, y)

# Save everything
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(le_soil, open("soil_encoder.pkl", "wb"))
pickle.dump(le_season, open("season_encoder.pkl", "wb"))
pickle.dump(le_crop, open("crop_encoder.pkl", "wb"))

print("✅ Model trained and saved!")