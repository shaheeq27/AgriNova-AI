import requests
from datetime import datetime, timedelta
#from database import get_cached_weather, store_weather


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

import time

def fetch_weather_data(lat, lon):

    end_date = datetime.today()

    chunks = [
        (end_date - timedelta(days=730), end_date - timedelta(days=540)),
        (end_date - timedelta(days=540), end_date - timedelta(days=360)),
        (end_date - timedelta(days=360), end_date - timedelta(days=180)),
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
            print("API chunk failed:", e)

            # fallback = use previous data if available
            if all_temps:
                avg_temp = sum(all_temps) / len(all_temps)
                avg_rain = sum(all_rain) / len(all_rain)
                avg_humidity = sum(all_humidity) / len(all_humidity)

                all_temps.extend([avg_temp]*30)
                all_rain.extend([avg_rain]*30)
                all_humidity.extend([avg_humidity]*30)
            else:
                # first chunk fallback
                all_temps.extend([25]*30)
                all_rain.extend([100]*30)
                all_humidity.extend([60]*30)

        # VERY IMPORTANT → avoid rate limit
        time.sleep(1)

    return all_temps, all_rain, all_humidity


        


def calculate_averages(temps, rain, humidity):

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