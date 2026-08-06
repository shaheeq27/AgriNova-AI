from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.schemas.common import APIResponse
from app.services.notification_service import NotificationService
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/")
@router.get("")
async def list_notifications(
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = NotificationService()
    items = await service.get_notifications(db, current_user.id, unread_only)
    unread_count = await service.get_unread_count(db, current_user.id)
    return APIResponse.success({
        "items": items,
        "total": len(items),
        "unread_count": unread_count
    })

@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = NotificationService()
    count = await service.get_unread_count(db, current_user.id)
    return APIResponse.success({"count": count})

@router.post("/generate")
async def generate_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = NotificationService()
    generated = await service.generate_notifications(db, current_user.id)
    return APIResponse.success({"generated_count": len(generated)})

@router.put("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = NotificationService()
    n = await service.mark_read(db, notification_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    return APIResponse.success(n)

@router.put("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = NotificationService()
    updated_count = await service.mark_all_read(db, current_user.id)
    return APIResponse.success({"updated_count": updated_count})
