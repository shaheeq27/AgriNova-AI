"""
AgriNova AI — Weather API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.weather_service import WeatherService
from app.services.farm_service import FarmService
from app.repositories.weather_repo import WeatherRepository


router = APIRouter(prefix="/weather", tags=["Weather"])

CITY_COORDS = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
}


@router.get("/farm/{farm_id}", response_model=APIResponse)
async def get_farm_weather(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    farm_service = FarmService(db)
    farm = await farm_service.get_farm(current_user.id, farm_id)
    
    lat = farm.latitude
    lng = farm.longitude
    
    if lat is None or lng is None:
        coords = CITY_COORDS.get(farm.location_city, (20.5937, 78.9629))
        lat, lng = coords

    weather_service = WeatherService()
    current = await weather_service.get_current_weather(lat, lng)
    forecast = await weather_service.get_forecast(lat, lng)
    alerts = await weather_service.get_weather_alerts(lat, lng)
    
    return APIResponse.success(data={
        "current": current,
        "forecast": forecast,
        "alerts": alerts
    })


@router.get("/farm/{farm_id}/history", response_model=APIResponse)
async def get_weather_history(
    farm_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    farm_service = FarmService(db)
    await farm_service.get_farm(current_user.id, farm_id)
    
    repo = WeatherRepository(db)
    history = await repo.get_history(farm_id, days)
    
    from app.schemas.weather import WeatherRecordResponse
    return APIResponse.success(
        data=[WeatherRecordResponse.model_validate(h).model_dump() for h in history]
    )
