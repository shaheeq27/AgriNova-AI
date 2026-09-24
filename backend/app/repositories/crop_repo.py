"""
AgriNova AI — Crop repository.

Database queries for Crop, CropTimeline, and DailyTask models.
"""

from datetime import date, datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.crop import Crop
from app.models.timeline import CropTimeline, DailyTask


class CropRepository:
    """Data access for crop lifecycle management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, crop: Crop) -> Crop:
        self.db.add(crop)
        await self.db.commit()
        await self.db.refresh(crop)
        return crop

    async def get_by_id(self, crop_id: str) -> Crop | None:
        result = await self.db.execute(
            select(Crop)
            .options(selectinload(Crop.timeline))
            .where(Crop.id == crop_id)
        )
        return result.scalar_one_or_none()

    async def get_by_farm_id(self, farm_id: str) -> list[Crop]:
        result = await self.db.execute(
            select(Crop)
            .where(Crop.farm_id == farm_id)
            .order_by(Crop.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, crop: Crop, **kwargs) -> Crop:
        for key, value in kwargs.items():
            if hasattr(crop, key):
                setattr(crop, key, value)
        crop.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(crop)
        return crop

    async def delete(self, crop: Crop) -> None:
        await self.db.delete(crop)
        await self.db.commit()

    # ── Timeline ──

    async def create_timeline_stage(self, stage: CropTimeline) -> CropTimeline:
        self.db.add(stage)
        await self.db.flush()
        return stage

    async def get_timeline(self, crop_id: str) -> list[CropTimeline]:
        result = await self.db.execute(
            select(CropTimeline)
            .options(selectinload(CropTimeline.tasks))
            .where(CropTimeline.crop_id == crop_id)
            .order_by(CropTimeline.stage_order)
        )
        return list(result.scalars().all())

    async def update_stage_status(self, stage_id: str, status: str) -> CropTimeline | None:
        result = await self.db.execute(
            select(CropTimeline).where(CropTimeline.id == stage_id)
        )
        stage = result.scalar_one_or_none()
        if stage:
            stage.status = status
            await self.db.commit()
            await self.db.refresh(stage)
        return stage

    # ── Daily Tasks ──

    async def create_task(self, task: DailyTask) -> DailyTask:
        self.db.add(task)
        await self.db.flush()
        return task

    async def get_tasks_by_crop(
        self, crop_id: str, filter_date: date | None = None
    ) -> list[DailyTask]:
        stmt = select(DailyTask).where(DailyTask.crop_id == crop_id)
        if filter_date:
            stmt = stmt.where(DailyTask.scheduled_date == filter_date)
        stmt = stmt.order_by(DailyTask.scheduled_date, DailyTask.priority)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_task(self, task_id: str) -> DailyTask | None:
        result = await self.db.execute(
            select(DailyTask).where(DailyTask.id == task_id)
        )
        return result.scalar_one_or_none()

    async def update_task(self, task_id: str, **kwargs) -> DailyTask | None:
        result = await self.db.execute(
            select(DailyTask).where(DailyTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            if kwargs.get("is_completed"):
                task.completed_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(task)
        return task

    async def commit(self):
        await self.db.commit()
