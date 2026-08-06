from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.activity_repo import ActivityRepository
from app.models.activity_log import ActivityLog

class ActivityService:
    def __init__(self, db: AsyncSession):
        self.repo = ActivityRepository(db)

    async def log_activity(self, user_id: str, action: str, entity_type: str, entity_id: str, description: str, farm_id: str = None, crop_id: str = None, metadata_json: str = None) -> ActivityLog:
        return await self.repo.create(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            farm_id=farm_id,
            crop_id=crop_id,
            metadata_json=metadata_json
        )

    async def get_feed(self, user_id: str, farm_id: str = None, crop_id: str = None, limit: int = 50, offset: int = 0) -> list[dict]:
        activities = await self.repo.get_feed(user_id, farm_id, crop_id, limit, offset)
        return [
            {
                "id": a.id,
                "user_id": a.user_id,
                "farm_id": a.farm_id,
                "crop_id": a.crop_id,
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "description": a.description,
                "metadata_json": a.metadata_json,
                "created_at": a.created_at
            }
            for a in activities
        ]

    async def get_count(self, user_id: str, farm_id: str = None) -> int:
        return await self.repo.get_count(user_id, farm_id)
