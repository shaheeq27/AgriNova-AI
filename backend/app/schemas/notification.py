from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    severity: str
    is_read: bool
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    unread_count: int

class UnreadCountResponse(BaseModel):
    count: int

class NotificationPreferenceResponse(BaseModel):
    email_enabled: bool
    weather_alerts: bool
    irrigation_reminders: bool
    fertilizer_reminders: bool
    market_alerts: bool
    ai_insights: bool

    class Config:
        from_attributes = True

class NotificationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    weather_alerts: Optional[bool] = None
    irrigation_reminders: Optional[bool] = None
    fertilizer_reminders: Optional[bool] = None
    market_alerts: Optional[bool] = None
    ai_insights: Optional[bool] = None
