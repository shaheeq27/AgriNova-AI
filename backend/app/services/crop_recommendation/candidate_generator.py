"""
AgriNova AI — Candidate Generator.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.knowledge import CropProfile

class CandidateGenerator:
    """
    Generates crop candidates for the recommendation engine.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_candidates(self) -> list[CropProfile]:
        """
        Query all available CropProfile records.
        """
        result = await self.db.execute(select(CropProfile))
        return list(result.scalars().all())
