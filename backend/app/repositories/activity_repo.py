from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity_log import ActivityLog

class ActivityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> ActivityLog:
        activity = ActivityLog(**kwargs)
        self.db.add(activity)
        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def get_feed(self, user_id: str, farm_id: str = None, crop_id: str = None, limit: int = 50, offset: int = 0) -> list[ActivityLog]:
        query = select(ActivityLog).where(ActivityLog.user_id == user_id)
        if farm_id:
            query = query.where(ActivityLog.farm_id == farm_id)
        if crop_id:
            query = query.where(ActivityLog.crop_id == crop_id)
            
        query = query.order_by(ActivityLog.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_count(self, user_id: str, farm_id: str = None) -> int:
        query = select(func.count(ActivityLog.id)).where(ActivityLog.user_id == user_id)
        if farm_id:
            query = query.where(ActivityLog.farm_id == farm_id)
            
        result = await self.db.execute(query)
        return result.scalar_one()
