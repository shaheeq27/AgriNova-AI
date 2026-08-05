"""
AgriNova AI — Weather repository.
"""

from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.weather import WeatherRecord


class WeatherRepository:
    """Data access layer for WeatherRecord model."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_record(self, record: WeatherRecord) -> WeatherRecord:
        """Insert a new weather record."""
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def get_by_farm_and_date(self, farm_id: str, target_date: date) -> WeatherRecord | None:
        """Fetch weather record by farm and date."""
        result = await self.db.execute(
            select(WeatherRecord).where(
                WeatherRecord.farm_id == farm_id,
                WeatherRecord.date == target_date
            )
        )
        return result.scalar_one_or_none()

    async def get_history(self, farm_id: str, days: int = 30) -> list[WeatherRecord]:
        """Fetch weather history for a farm."""
        start_date = date.today() - timedelta(days=days)
        result = await self.db.execute(
            select(WeatherRecord)
            .where(
                WeatherRecord.farm_id == farm_id,
                WeatherRecord.date >= start_date
            )
            .order_by(WeatherRecord.date.desc())
        )
        return list(result.scalars().all())
