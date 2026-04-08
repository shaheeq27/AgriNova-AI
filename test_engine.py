from scoring_engine import rank_crops

results = rank_crops(
    temp=24,
    rain=90,
    humidity=65,
    soil="Loamy",
    season="Kharif"
)

print(results)