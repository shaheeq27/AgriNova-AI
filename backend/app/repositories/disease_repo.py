"""
AgriNova AI — Disease repository.

Database operations for DiseaseRecord and DiseaseImage models.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.disease import DiseaseImage, DiseaseRecord


class DiseaseRepository:
    """Data access layer for DiseaseRecord and DiseaseImage models."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_record(self, record: DiseaseRecord) -> DiseaseRecord:
        """Insert a new disease record."""
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def get_by_id(self, record_id: str) -> DiseaseRecord | None:
        """Fetch disease record by ID with images loaded."""
        result = await self.db.execute(
            select(DiseaseRecord)
            .options(selectinload(DiseaseRecord.images))
            .where(DiseaseRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def get_by_crop_id(self, crop_id: str) -> list[DiseaseRecord]:
        """Fetch all disease records for a crop."""
        result = await self.db.execute(
            select(DiseaseRecord)
            .options(selectinload(DiseaseRecord.images))
            .where(DiseaseRecord.crop_id == crop_id)
            .order_by(DiseaseRecord.detected_at.desc())
        )
        return list(result.scalars().all())

    async def update_record(self, record: DiseaseRecord, **kwargs) -> DiseaseRecord:
        """Update disease record fields."""
        for key, value in kwargs.items():
            if hasattr(record, key) and value is not None:
                setattr(record, key, value)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def create_image(self, image: DiseaseImage) -> DiseaseImage:
        """Insert a new disease image."""
        self.db.add(image)
        await self.db.flush()
        await self.db.refresh(image)
        return image
