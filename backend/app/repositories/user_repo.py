"""
AgriNova AI — User repository.

Database operations for the User model.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Data access layer for User model."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        """Insert a new user."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        """Fetch user by primary key."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Fetch user by email address."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def update(self, user: User, **kwargs) -> User:
        """Update user fields."""
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user
