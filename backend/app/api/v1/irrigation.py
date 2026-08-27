"""
AgriNova AI — Irrigation API routes.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.irrigation import IrrigationLogCreate
from app.services.irrigation_engine import IrrigationEngine
from app.services.farm_service import FarmService
from app.services.weather_service import WeatherService


router = APIRouter(prefix="/irrigation", tags=["Irrigation"])

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


@router.get("/recommend/{crop_name}", response_model=APIResponse)
async def get_irrigation_recommendation(
    crop_name: str,
    stage: str = Query(...),
    soil_type: str = Query(...),
    farm_id: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_weather = None
    historical_insights = None
    if farm_id:
        from app.services.farm_service import FarmService
        farm_service = FarmService(db)
        try:
            farm = await farm_service.get_farm(current_user.id, farm_id)
            lat = farm.latitude
            lng = farm.longitude
            if lat is None or lng is None:
                coords = CITY_COORDS.get(farm.location_city, (20.5937, 78.9629))
                lat, lng = coords

            weather_service = WeatherService()
            current_weather = await weather_service.get_current_weather(lat, lng)

            from app.ai.services.historical_insights_service import HistoricalInsightsService
            insights_service = HistoricalInsightsService()
            historical_insights = await insights_service.compute_insights_context(db, farm_id)
        except Exception:
            pass

    engine = IrrigationEngine()
    recommendation = await engine.get_recommendation(db, crop_name, stage, soil_type, current_weather, historical_insights)
    return APIResponse.success(data=recommendation)


@router.post("/log", response_model=APIResponse)
async def log_irrigation(
    data: IrrigationLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    engine = IrrigationEngine()
    log = await engine.log_irrigation(db, current_user.id, data.crop_id, data)
    return APIResponse.success(data=log.model_dump(), message="Irrigation log created")


@router.get("/logs/{crop_id}", response_model=APIResponse)
async def get_irrigation_logs(
    crop_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    engine = IrrigationEngine()
    logs = await engine.get_logs(db, crop_id)
    return APIResponse.success(data=[log.model_dump() for log in logs])
