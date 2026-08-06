from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta
from app.repositories.notification_repo import NotificationRepository
from app.models.notification import Notification
from app.models.timeline import DailyTask, CropTimeline
from app.models.weather import WeatherRecord
from app.models.farm import Farm

class NotificationService:
    def __init__(self):
        pass

    async def generate_notifications(self, db: AsyncSession, user_id: str) -> list[dict]:
        repo = NotificationRepository(db)
        generated = []
        today = datetime.now(timezone.utc).date()
        
        # Check existing notifications for today to avoid duplicates
        existing_query = select(Notification).where(
            Notification.user_id == user_id,
            func.date(Notification.created_at) == today
        )
        existing_res = await db.execute(existing_query)
        existing_nots = existing_res.scalars().all()
        existing_keys = set(f"{n.type}_{n.related_entity_id}" for n in existing_nots)

        # 1. DailyTask Overdue
        tasks_query = select(DailyTask).where(
            DailyTask.is_completed == False,
            func.date(DailyTask.scheduled_date) < today
        )
        tasks_res = await db.execute(tasks_query)
        for task in tasks_res.scalars().all():
            key = f"task_overdue_{task.id}"
            if key not in existing_keys:
                n = await repo.create(
                    user_id=user_id,
                    title="Task Overdue",
                    message=f"Task '{task.title}' is overdue.",
                    type="task_overdue",
                    severity="warning",
                    related_entity_type="task",
                    related_entity_id=task.id
                )
                generated.append(n)
                existing_keys.add(key)

        # 2. DailyTask Irrigation & Fertilizer
        tasks_today_query = select(DailyTask).where(
            DailyTask.is_completed == False,
            func.date(DailyTask.scheduled_date) == today
        )
        tasks_today_res = await db.execute(tasks_today_query)
        for task in tasks_today_res.scalars().all():
            ntype = None
            if task.category == 'irrigation':
                ntype = 'irrigation_reminder'
                title = "Irrigation Due"
            elif task.category == 'fertilizer':
                ntype = 'fertilizer_due'
                title = "Fertilizer Due"
            
            if ntype:
                key = f"{ntype}_{task.id}"
                if key not in existing_keys:
                    n = await repo.create(
                        user_id=user_id,
                        title=title,
                        message=f"Task '{task.title}' is scheduled for today.",
                        type=ntype,
                        severity="info",
                        related_entity_type="task",
                        related_entity_id=task.id
                    )
                    generated.append(n)
                    existing_keys.add(key)

        # 4. Harvest Reminder
        harvest_query = select(CropTimeline).where(
            CropTimeline.stage_name == 'Maturity',
            CropTimeline.status == 'active'
        )
        harvest_res = await db.execute(harvest_query)
        for timeline in harvest_res.scalars().all():
            key = f"harvest_reminder_{timeline.crop_id}"
            if key not in existing_keys:
                n = await repo.create(
                    user_id=user_id,
                    title="Harvest Reminder",
                    message="A crop is in the Maturity stage and ready for harvest.",
                    type="harvest_reminder",
                    severity="info",
                    related_entity_type="crop",
                    related_entity_id=timeline.crop_id
                )
                generated.append(n)
                existing_keys.add(key)

        # 5. Weather Alert
        weather_query = select(WeatherRecord).join(Farm).where(
            Farm.user_id == user_id,
            WeatherRecord.date == today
        )
        weather_res = await db.execute(weather_query)
        for weather in weather_res.scalars().all():
            key = f"weather_alert_{weather.farm_id}"
            if key not in existing_keys:
                if weather.temp_avg and (weather.temp_avg > 35 or weather.temp_avg < 0):
                    n = await repo.create(
                        user_id=user_id,
                        title="Weather Alert",
                        message=f"Extreme temperature detected: {weather.temp_avg}°C",
                        type="weather_alert",
                        severity="critical",
                        related_entity_type="farm",
                        related_entity_id=weather.farm_id
                    )
                    generated.append(n)
                    existing_keys.add(key)
        
        return [
            {
                "id": g.id,
                "title": g.title,
                "message": g.message,
                "type": g.type,
                "severity": g.severity,
                "is_read": g.is_read,
                "related_entity_type": g.related_entity_type,
                "related_entity_id": g.related_entity_id,
                "created_at": g.created_at
            } for g in generated
        ]

    async def get_notifications(self, db: AsyncSession, user_id: str, unread_only: bool = False) -> list[dict]:
        repo = NotificationRepository(db)
        items = await repo.get_all(user_id, unread_only)
        return [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "severity": n.severity,
                "is_read": n.is_read,
                "related_entity_type": n.related_entity_type,
                "related_entity_id": n.related_entity_id,
                "created_at": n.created_at
            } for n in items
        ]

    async def mark_read(self, db: AsyncSession, notification_id: str) -> dict:
        repo = NotificationRepository(db)
        n = await repo.mark_read(notification_id)
        if not n:
            return None
        return {
            "id": n.id,
            "is_read": n.is_read
        }

    async def mark_all_read(self, db: AsyncSession, user_id: str) -> int:
        repo = NotificationRepository(db)
        return await repo.mark_all_read(user_id)

    async def get_unread_count(self, db: AsyncSession, user_id: str) -> int:
        repo = NotificationRepository(db)
        return await repo.get_unread_count(user_id)
