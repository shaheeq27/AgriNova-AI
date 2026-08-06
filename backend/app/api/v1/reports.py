"""
AgriNova AI — Reports API router.

Endpoints for generating structured farm operation reports.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/crop/{crop_id}")
async def crop_report(
    crop_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a comprehensive crop report."""
    service = ReportService(db)
    data = await service.generate_crop_report(current_user.id, crop_id)
    return APIResponse.success(data)


@router.get("/farm/{farm_id}")
async def farm_report(
    farm_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a comprehensive farm report."""
    service = ReportService(db)
    data = await service.generate_farm_report(current_user.id, farm_id)
    return APIResponse.success(data)


@router.get("/weather/{farm_id}")
async def weather_report(
    farm_id: str,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a weather report for a farm."""
    service = ReportService(db)
    data = await service.generate_weather_report(current_user.id, farm_id, days)
    return APIResponse.success(data)


@router.get("/fertilizer/{crop_id}")
async def fertilizer_report(
    crop_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a fertilizer application report."""
    service = ReportService(db)
    data = await service.generate_fertilizer_report(current_user.id, crop_id)
    return APIResponse.success(data)


@router.get("/irrigation/{crop_id}")
async def irrigation_report(
    crop_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate an irrigation application report."""
    service = ReportService(db)
    data = await service.generate_irrigation_report(current_user.id, crop_id)
    return APIResponse.success(data)
