"""
AgriNova AI — Weather schemas.
"""

from datetime import date
from pydantic import BaseModel


class WeatherCurrent(BaseModel):
    temperature: float
    humidity: float
    rainfall: float
    wind_speed: float
    condition: str
    description: str
    source: str


class WeatherForecast(BaseModel):
    date: date
    temp_min: float
    temp_max: float
    precipitation: float
    wind_speed: float
    condition: str


class WeatherAlert(BaseModel):
    type: str
    severity: str
    message: str
    date: date


class WeatherResponse(BaseModel):
    current: WeatherCurrent
    forecast: list[WeatherForecast]
    alerts: list[WeatherAlert]


class WeatherRecordResponse(BaseModel):
    id: str
    farm_id: str
    date: date
    temp_avg: float
    humidity: float | None
    rainfall: float
    wind_speed: float | None
    condition: str | None
    source: str

    model_config = {"from_attributes": True}
