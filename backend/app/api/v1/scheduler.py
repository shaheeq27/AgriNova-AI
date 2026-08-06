from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])

@router.get("/daily")
async def get_daily(
    date: str = Query(..., description="YYYY-MM-DD"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SchedulerService(db)
    data = await service.get_daily(current_user.id, date)
    return APIResponse.success(data=data)

@router.get("/weekly")
async def get_weekly(
    start: str = Query(..., description="YYYY-MM-DD"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SchedulerService(db)
    data = await service.get_weekly(current_user.id, start)
    return APIResponse.success(data=data)

@router.get("/monthly")
async def get_monthly(
    year: int = Query(...),
    month: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SchedulerService(db)
    data = await service.get_monthly(current_user.id, year, month)
    return APIResponse.success(data=data)

@router.get("/crop-events")
async def get_crop_events(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SchedulerService(db)
    data = await service.get_crop_events(current_user.id)
    return APIResponse.success(data=data)
