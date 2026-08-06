from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.schemas.common import APIResponse
from app.services.activity_service import ActivityService
from app.models.user import User

router = APIRouter(prefix="/activity", tags=["Activity"])

@router.get("/")
@router.get("")
async def get_activity_feed(
    farm_id: Optional[str] = None,
    crop_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ActivityService(db)
    items = await service.get_feed(current_user.id, farm_id, crop_id, limit, offset)
    total = await service.get_count(current_user.id, farm_id)
    return APIResponse.success({"items": items, "total": total})

@router.get("/farm/{farm_id}")
async def get_farm_activity_feed(
    farm_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ActivityService(db)
    items = await service.get_feed(current_user.id, farm_id, None, limit, offset)
    total = await service.get_count(current_user.id, farm_id)
    return APIResponse.success({"items": items, "total": total})

@router.get("/crop/{crop_id}")
async def get_crop_activity_feed(
    crop_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ActivityService(db)
    items = await service.get_feed(current_user.id, None, crop_id, limit, offset)
    return APIResponse.success({"items": items, "total": len(items)})
