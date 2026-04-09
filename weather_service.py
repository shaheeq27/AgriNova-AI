import requests
import time
from datetime import datetime, timedelta


def get_coordinates(city):

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    if "results" not in data:
        raise ValueError("City not found")

    lat = data["results"][0]["latitude"]
    lon = data["results"][0]["longitude"]

    return lat, lon


def fetch_weather_data(lat, lon):

    end_date = datetime.today()

    # ✅ 1-year data split into 2 safe chunks
    chunks = [
        (end_date - timedelta(days=365), end_date - timedelta(days=180)),
        (end_date - timedelta(days=180), end_date)
    ]

    all_temps = []
    all_rain = []
    all_humidity = []

    for start, end in chunks:

        url = (
            f"https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={lat}&longitude={lon}"
            f"&start_date={start.date()}"
            f"&end_date={end.date()}"
            f"&daily=temperature_2m_mean,precipitation_sum,relative_humidity_2m_mean"
        )

        try:
            print(f"Fetching data: {start.date()} to {end.date()}")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            temps = data["daily"]["temperature_2m_mean"]
            rain = data["daily"]["precipitation_sum"]
            humidity = data["daily"]["relative_humidity_2m_mean"]

            all_temps.extend(temps)
            all_rain.extend(rain)
            all_humidity.extend(humidity)

        except Exception as e:
            print("API failed for chunk:", e)
            continue  # ✅ skip failed chunk (DO NOT add fake data)

        # ✅ avoid rate limiting
        time.sleep(1)

    return all_temps, all_rain, all_humidity


def calculate_averages(temps, rain, humidity):

    # ✅ final fallback ONLY if everything failed
    if not temps or not rain or not humidity:
        print("Using fallback climate data")
        return 25, 100, 60

    avg_temp = sum(temps) / len(temps)
    avg_rain = sum(rain) / len(rain)
    avg_humidity = sum(humidity) / len(humidity)

    return round(avg_temp, 2), round(avg_rain, 2), round(avg_humidity, 2)


def get_climate_data(city):

    lat, lon = get_coordinates(city)

    temps, rain, humidity = fetch_weather_data(lat, lon)

    avg_temp, avg_rain, avg_humidity = calculate_averages(
        temps, rain, humidity
    )

    return {
        "temperature": avg_temp,
        "rainfall": avg_rain,
        "humidity": avg_humidity
    }