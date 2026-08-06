from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ActivityLogResponse(BaseModel):
    id: str
    user_id: str
    farm_id: Optional[str] = None
    crop_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    description: str
    metadata_json: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class ActivityFeedResponse(BaseModel):
    items: List[ActivityLogResponse]
    total: int
