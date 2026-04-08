import requests
from datetime import datetime, timedelta
from database import get_cached_weather, store_weather


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
    start_date = end_date - timedelta(days=730)

    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start_date.date()}"
        f"&end_date={end_date.date()}"
        f"&daily=temperature_2m_mean,precipitation_sum,relative_humidity_2m_mean"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    temps = data["daily"]["temperature_2m_mean"]
    rain = data["daily"]["precipitation_sum"]
    humidity = data["daily"]["relative_humidity_2m_mean"]

    return temps, rain, humidity


def calculate_averages(temps, rain, humidity):

    avg_temp = sum(temps) / len(temps)
    avg_rain = sum(rain) / len(rain)
    avg_humidity = sum(humidity) / len(humidity)

    return round(avg_temp, 2), round(avg_rain, 2), round(avg_humidity, 2)


def get_climate_data(city):

    cached = get_cached_weather(city)

    if cached:
        print("Using cached weather data")
        return cached

    print("Fetching weather from API")

    lat, lon = get_coordinates(city)

    temps, rain, humidity = fetch_weather_data(lat, lon)

    avg_temp, avg_rain, avg_humidity = calculate_averages(
        temps, rain, humidity
    )

    store_weather(city, avg_temp, avg_rain, avg_humidity)

    return {
        "temperature": avg_temp,
        "rainfall": avg_rain,
        "humidity": avg_humidity
    }