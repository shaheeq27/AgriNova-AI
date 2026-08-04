"""
AgriNova AI — Farm repository.

Database operations for the Farm model.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.farm import Farm


class FarmRepository:
    """Data access layer for Farm model."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, farm: Farm) -> Farm:
        """Insert a new farm."""
        self.db.add(farm)
        await self.db.flush()
        await self.db.refresh(farm)
        return farm

    async def get_by_id(self, farm_id: str) -> Farm | None:
        """Fetch farm by primary key with crops loaded."""
        result = await self.db.execute(
            select(Farm)
            .options(selectinload(Farm.crops))
            .where(Farm.id == farm_id, Farm.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> list[Farm]:
        """Fetch all active farms for a user."""
        result = await self.db.execute(
            select(Farm)
            .options(selectinload(Farm.crops))
            .where(Farm.user_id == user_id, Farm.is_active == True)
            .order_by(Farm.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_by_user_id(self, user_id: str) -> int:
        """Count active farms for a user."""
        result = await self.db.execute(
            select(func.count(Farm.id)).where(
                Farm.user_id == user_id, Farm.is_active == True
            )
        )
        return result.scalar_one()

    async def update(self, farm: Farm, **kwargs) -> Farm:
        """Update farm fields."""
        for key, value in kwargs.items():
            if hasattr(farm, key) and value is not None:
                setattr(farm, key, value)
        await self.db.flush()
        await self.db.refresh(farm)
        return farm

    async def soft_delete(self, farm: Farm) -> Farm:
        """Soft-delete a farm by setting is_active = False."""
        farm.is_active = False
        await self.db.flush()
        return farm
