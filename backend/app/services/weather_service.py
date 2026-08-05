"""
AgriNova AI — Weather service.
"""

import httpx
from datetime import datetime, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather import WeatherRecord
from app.repositories.weather_repo import WeatherRepository


class WeatherService:
    async def _fetch_weather_data(self, latitude: float, longitude: float, days: int = 7) -> dict:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
            "timezone": "auto",
            "forecast_days": days
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except Exception:
            return self._get_mock_weather(days)

    def _get_mock_weather(self, days: int) -> dict:
        return {
            "current_weather": {
                "temperature": 25.5,
                "windspeed": 12.0,
                "time": datetime.now(timezone.utc).isoformat()
            },
            "daily": {
                "time": [date.today().isoformat()] * days,
                "temperature_2m_min": [18.0] * days,
                "temperature_2m_max": [30.0] * days,
                "precipitation_sum": [5.0] * days,
                "windspeed_10m_max": [15.0] * days,
            },
            "source": "demo"
        }

    async def get_current_weather(self, latitude: float, longitude: float) -> dict:
        data = await self._fetch_weather_data(latitude, longitude, days=1)
        source = data.get("source", "open-meteo")
        
        current = data.get("current_weather", {})
        daily = data.get("daily", {})
        
        precipitation = daily.get("precipitation_sum", [0.0])[0] if daily.get("precipitation_sum") else 0.0
        
        return {
            "temperature": current.get("temperature", 25.0),
            "humidity": 60.0,
            "rainfall": precipitation,
            "wind_speed": current.get("windspeed", 10.0),
            "condition": "Clear",
            "description": "Clear skies",
            "source": source
        }

    async def get_forecast(self, latitude: float, longitude: float, days: int = 7) -> list[dict]:
        data = await self._fetch_weather_data(latitude, longitude, days)
        daily = data.get("daily", {})
        
        times = daily.get("time", [])
        temp_mins = daily.get("temperature_2m_min", [])
        temp_maxs = daily.get("temperature_2m_max", [])
        precips = daily.get("precipitation_sum", [])
        winds = daily.get("windspeed_10m_max", [])
        
        forecast = []
        for i in range(len(times)):
            forecast.append({
                "date": times[i] if i < len(times) else date.today().isoformat(),
                "temp_min": temp_mins[i] if i < len(temp_mins) else 0.0,
                "temp_max": temp_maxs[i] if i < len(temp_maxs) else 0.0,
                "precipitation": precips[i] if i < len(precips) else 0.0,
                "wind_speed": winds[i] if i < len(winds) else 0.0,
                "condition": "Clear"
            })
        return forecast

    async def get_weather_alerts(self, latitude: float, longitude: float) -> list[dict]:
        forecasts = await self.get_forecast(latitude, longitude, days=3)
        alerts = []
        for f in forecasts:
            if f["precipitation"] > 50:
                alerts.append({
                    "type": "rain",
                    "severity": "critical",
                    "message": f"Heavy rain expected ({f['precipitation']}mm)",
                    "date": f["date"]
                })
            if f["temp_min"] < 2:
                alerts.append({
                    "type": "frost",
                    "severity": "warning",
                    "message": f"Frost warning (low of {f['temp_min']}°C)",
                    "date": f["date"]
                })
            if f["wind_speed"] > 40:
                alerts.append({
                    "type": "wind",
                    "severity": "warning",
                    "message": f"High winds expected ({f['wind_speed']} km/h)",
                    "date": f["date"]
                })
            if f["temp_max"] > 40:
                alerts.append({
                    "type": "heat",
                    "severity": "critical",
                    "message": f"Extreme heat alert (high of {f['temp_max']}°C)",
                    "date": f["date"]
                })
        return alerts

    async def save_weather_record(self, db: AsyncSession, farm_id: str, weather_data: dict) -> WeatherRecord:
        repo = WeatherRepository(db)
        record = WeatherRecord(
            farm_id=farm_id,
            date=date.today(),
            temp_min=weather_data.get("temp_min"),
            temp_max=weather_data.get("temp_max"),
            temp_avg=weather_data.get("temperature", 25.0),
            humidity=weather_data.get("humidity"),
            rainfall=weather_data.get("rainfall", 0.0),
            wind_speed=weather_data.get("wind_speed"),
            condition=weather_data.get("condition"),
            source=weather_data.get("source", "open-meteo")
        )
        return await repo.save_record(record)
