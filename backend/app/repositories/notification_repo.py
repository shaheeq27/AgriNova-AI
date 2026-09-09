from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification

class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> Notification:
        notification = Notification(**kwargs)
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_all(self, user_id: str, unread_only: bool = False, skip: int = 0, limit: int = 50, category: str = None) -> list[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        if category:
            # Map category to notification types based on our taxonomy
            category_map = {
                "weather": ["weather_alert"],
                "irrigation": ["irrigation_reminder"],
                "fertilizer": ["fertilizer_reminder"],
                "market": ["market_alert"],
                "ai": ["ai_recommendation"],
                "system": ["welcome"],
            }
            if category in category_map:
                query = query.where(Notification.type.in_(category_map[category]))
            
        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: str) -> int:
        query = select(func.count(Notification.id)).where(
            Notification.user_id == user_id, 
            Notification.is_read == False
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def mark_read(self, notification_id: str, user_id: str) -> Notification | None:
        query = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
        result = await self.db.execute(query)
        notification = result.scalar_one_or_none()
        if notification:
            notification.is_read = True
            await self.db.commit()
            await self.db.refresh(notification)
        return notification

    async def mark_all_read(self, user_id: str) -> int:
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
