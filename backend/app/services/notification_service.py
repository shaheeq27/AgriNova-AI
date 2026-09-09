from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta
from app.repositories.notification_repo import NotificationRepository
from app.models.notification import Notification
from app.models.timeline import DailyTask, CropTimeline
from app.models.weather import WeatherRecord
from app.models.farm import Farm
from app.services.email_service import EmailService

import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        pass

    async def generate_notifications(self, db: AsyncSession, user_id: str) -> list[dict]:
        repo = NotificationRepository(db)
        email_service = EmailService(db)
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
                # task_overdue is NOT in EMAIL_ELIGIBLE_TYPES → no email

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
                ntype = 'fertilizer_reminder'
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

                    # Email sidecar — only if eligible + enabled + opted in
                    await email_service.maybe_send_email(
                        user_id=user_id,
                        notification_type=ntype,
                        title=title,
                        message=f"Task '{task.title}' is scheduled for today.",
                        template_data={"task_title": task.title},
                    )

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
                # harvest_reminder is NOT in EMAIL_ELIGIBLE_TYPES → no email

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
                    title = "Weather Alert"
                    message = f"Extreme temperature detected: {weather.temp_avg}°C"
                    n = await repo.create(
                        user_id=user_id,
                        title=title,
                        message=message,
                        type="weather_alert",
                        severity="critical",
                        related_entity_type="farm",
                        related_entity_id=weather.farm_id
                    )
                    generated.append(n)
                    existing_keys.add(key)

                    # Email sidecar for weather alerts
                    await email_service.maybe_send_email(
                        user_id=user_id,
                        notification_type="weather_alert",
                        title=title,
                        message=message,
                        template_data={
                            "farm_name": "Your Farm",
                            "severity": "critical",
                            "condition": "Extreme Temperature",
                            "temperature": weather.temp_avg,
                        },
                    )
        
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

    async def create_market_alert(
        self,
        db: AsyncSession,
        user_id: str,
        commodity: str,
        market_name: str,
        modal_price: float,
        price_change_pct: float,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> dict | None:
        """Create a market price alert notification with optional email.

        Called by MarketService when a price change exceeds the threshold.
        Returns the created notification dict, or None if duplicate.
        """
        repo = NotificationRepository(db)
        today = datetime.now(timezone.utc).date()

        # Dedup key: one alert per commodity per market per day
        dedup_key = f"market_alert_{commodity}_{market_name}"
        existing_query = select(Notification).where(
            Notification.user_id == user_id,
            Notification.type == "market_alert",
            func.date(Notification.created_at) == today
        )
        existing_res = await db.execute(existing_query)
        existing_keys = set(
            f"market_alert_{n.related_entity_type}_{n.related_entity_id}"
            for n in existing_res.scalars().all()
        )
        if dedup_key in existing_keys:
            return None

        direction = "up" if price_change_pct > 0 else "down"
        title = f"{commodity} price {direction} {abs(price_change_pct):.1f}%"
        message = (
            f"{commodity} at {market_name}: ₹{modal_price}/q "
            f"({'↑' if price_change_pct > 0 else '↓'}{abs(price_change_pct):.1f}% vs yesterday)"
        )

        # In-app notification
        n = await repo.create(
            user_id=user_id,
            title=title,
            message=message,
            type="market_alert",
            severity="warning" if abs(price_change_pct) > 15 else "info",
            related_entity_type=commodity,
            related_entity_id=market_name,
        )

        # Email sidecar
        email_service = EmailService(db)
        await email_service.maybe_send_email(
            user_id=user_id,
            notification_type="market_alert",
            title=title,
            message=message,
            template_data={
                "commodity": commodity,
                "market_name": market_name,
                "modal_price": modal_price,
                "price_change_pct": price_change_pct,
                "min_price": min_price,
                "max_price": max_price,
            },
        )

        return {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "severity": n.severity,
            "is_read": n.is_read,
            "related_entity_type": n.related_entity_type,
            "related_entity_id": n.related_entity_id,
            "created_at": n.created_at,
        }

    async def get_notifications(self, db: AsyncSession, user_id: str, unread_only: bool = False, skip: int = 0, limit: int = 50, category: str = None) -> list[dict]:
        repo = NotificationRepository(db)
        items = await repo.get_all(user_id, unread_only, skip, limit, category)
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

    async def mark_read(self, db: AsyncSession, notification_id: str, user_id: str) -> dict:
        repo = NotificationRepository(db)
        n = await repo.mark_read(notification_id, user_id)
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
