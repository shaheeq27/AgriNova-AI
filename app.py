from flask import Flask, render_template, request
from weather_service import get_climate_data
from scoring_engine import rank_crops
from ml_engine import predict_crop

app = Flask(__name__)


# 👉 Welcome page
@app.route("/")
def welcome():
    return render_template("welcome.html")


# 👉 Main page
@app.route("/index", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        city = request.form["city"]
        soil = request.form["soil"]
        season = request.form["season"]
        farm_size = request.form.get("farm_size")

        try:
            climate = get_climate_data(city)
        except ValueError:
            return render_template("index.html", error="City not found")

        avg_temp = climate["temperature"]
        avg_rain = climate["rainfall"]
        avg_humidity = climate["humidity"]

        # 🤖 ML predictions (Top 3)
        ml_predictions = predict_crop(
            avg_temp,
            avg_rain,
            avg_humidity,
            soil,
            season
        )

        # 📊 Rule-based recommendations
        recommendations = rank_crops(
            avg_temp,
            avg_rain,
            avg_humidity,
            soil,
            season
        )

        # 🌱 Fertilizer calculation
        if farm_size:
            try:
                farm_size = float(farm_size)
            except:
                farm_size = None

        for crop in recommendations:
            if farm_size:
                crop["fertilizer_needed"] = round(
                    crop["fertilizer_per_acre"] * farm_size, 2
                )
            else:
                crop["fertilizer_needed"] = None

        return render_template(
            "result.html",
            city=city,
            temperature=avg_temp,
            rainfall=avg_rain,
            humidity=avg_humidity,
            crops=recommendations,
            ml_predictions=ml_predictions   # ✅ correct variable
        )

    # 👉 GET request → show form
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
    