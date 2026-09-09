from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.schemas.common import APIResponse
from app.schemas.notification import NotificationPreferenceResponse, NotificationPreferenceUpdate
from app.models.user import User
from app.models.notification_preference import NotificationPreference

router = APIRouter(prefix="/preferences", tags=["Preferences"])

@router.get("/notifications", response_model=None)
async def get_notification_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(NotificationPreference).where(NotificationPreference.user_id == current_user.id)
    result = await db.execute(query)
    prefs = result.scalar_one_or_none()
    
    if not prefs:
        # Return defaults if no row exists yet
        prefs = NotificationPreference(
            user_id=current_user.id,
            email_enabled=True,
            weather_alerts=True,
            irrigation_reminders=True,
            fertilizer_reminders=True,
            market_alerts=True,
            ai_insights=True
        )
        
    return APIResponse.success({
        "email_enabled": prefs.email_enabled,
        "weather_alerts": prefs.weather_alerts,
        "irrigation_reminders": prefs.irrigation_reminders,
        "fertilizer_reminders": prefs.fertilizer_reminders,
        "market_alerts": prefs.market_alerts,
        "ai_insights": prefs.ai_insights
    })

@router.put("/notifications", response_model=None)
async def update_notification_preferences(
    update_data: NotificationPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(NotificationPreference).where(NotificationPreference.user_id == current_user.id)
    result = await db.execute(query)
    prefs = result.scalar_one_or_none()
    
    if not prefs:
        prefs = NotificationPreference(
            user_id=current_user.id,
            email_enabled=True,
            weather_alerts=True,
            irrigation_reminders=True,
            fertilizer_reminders=True,
            market_alerts=True,
            ai_insights=True
        )
        db.add(prefs)
        
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(prefs, key, value)
        
    await db.commit()
    await db.refresh(prefs)
    
    return APIResponse.success({
        "email_enabled": prefs.email_enabled,
        "weather_alerts": prefs.weather_alerts,
        "irrigation_reminders": prefs.irrigation_reminders,
        "fertilizer_reminders": prefs.fertilizer_reminders,
        "market_alerts": prefs.market_alerts,
        "ai_insights": prefs.ai_insights
    })
