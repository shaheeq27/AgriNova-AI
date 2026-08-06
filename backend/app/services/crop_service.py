"""
AgriNova AI — Crop lifecycle service.

Business logic for planting crops, managing lifecycle, and ownership checks.
"""

from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.crop import Crop
from app.repositories.crop_repo import CropRepository
from app.repositories.farm_repo import FarmRepository
from app.schemas.crop import (
    CropCreate, CropListResponse, CropResponse, CropUpdate,
    DailyTaskResponse, DailyTaskUpdate, TaskListResponse,
)
from app.services import timeline_service
from app.services.activity_service import ActivityService


class CropService:
    """Crop lifecycle business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CropRepository(db)
        self.farm_repo = FarmRepository(db)

    async def _check_farm_ownership(self, user_id: str, farm_id: str):
        """Validate that the user owns the farm."""
        farm = await self.farm_repo.get_by_id(farm_id)
        if not farm:
            raise NotFoundException("Farm", farm_id)
        if farm.user_id != user_id:
            raise ForbiddenException("You do not have access to this farm")
        return farm

    async def _check_crop_ownership(self, user_id: str, crop_id: str) -> Crop:
        """Validate that the user owns the crop (via farm)."""
        crop = await self.repo.get_by_id(crop_id)
        if not crop:
            raise NotFoundException("Crop", crop_id)
        await self._check_farm_ownership(user_id, crop.farm_id)
        return crop

    async def create_crop(self, user_id: str, data: CropCreate) -> CropResponse:
        """Plant a new crop on a farm.

        Creates the crop record, generates a timeline from KB,
        and sets expected harvest date.
        """
        await self._check_farm_ownership(user_id, data.farm_id)

        planting = data.planting_date or date.today()

        crop = Crop(
            farm_id=data.farm_id,
            crop_name=data.crop_name,
            season=data.season,
            area_acres=data.area_acres,
            planting_date=planting,
            status="active",
            recommendation_score=data.recommendation_score,
            recommendation_source=data.recommendation_source,
            notes=data.notes,
        )
        crop = await self.repo.create(crop)

        # Generate timeline from Knowledge Base
        stages = await timeline_service.generate_timeline(
            self.db, crop.id, crop.crop_name, planting
        )

        # Set expected harvest date from last stage
        if stages:
            crop = await self.repo.update(
                crop, expected_harvest_date=stages[-1].end_date
            )

        # Log activity
        activity = ActivityService(self.db)
        await activity.log_activity(
            user_id=user_id,
            action="crop_planted",
            entity_type="crop",
            entity_id=crop.id,
            description=f"Planted '{crop.crop_name}' on farm",
            farm_id=data.farm_id,
            crop_id=crop.id,
        )

        return CropResponse.model_validate(crop)

    async def get_crop(self, user_id: str, crop_id: str) -> CropResponse:
        """Get a crop by ID with ownership check."""
        crop = await self._check_crop_ownership(user_id, crop_id)
        return CropResponse.model_validate(crop)

    async def list_crops(self, user_id: str, farm_id: str) -> CropListResponse:
        """List all crops for a farm."""
        await self._check_farm_ownership(user_id, farm_id)
        crops = await self.repo.get_by_farm_id(farm_id)
        return CropListResponse(
            crops=[CropResponse.model_validate(c) for c in crops],
            total=len(crops),
        )

    async def update_crop(
        self, user_id: str, crop_id: str, data: CropUpdate
    ) -> CropResponse:
        """Update a crop with ownership check."""
        crop = await self._check_crop_ownership(user_id, crop_id)
        update_data = data.model_dump(exclude_unset=True)
        crop = await self.repo.update(crop, **update_data)

        # Log activity
        activity = ActivityService(self.db)
        await activity.log_activity(
            user_id=user_id,
            action="crop_updated",
            entity_type="crop",
            entity_id=crop.id,
            description=f"Updated crop '{crop.crop_name}'",
            farm_id=crop.farm_id,
            crop_id=crop.id,
        )

        return CropResponse.model_validate(crop)

    async def delete_crop(self, user_id: str, crop_id: str) -> None:
        """Delete a crop with ownership check."""
        crop = await self._check_crop_ownership(user_id, crop_id)

        # Log activity before deletion
        activity = ActivityService(self.db)
        await activity.log_activity(
            user_id=user_id,
            action="crop_deleted",
            entity_type="crop",
            entity_id=crop_id,
            description=f"Deleted crop '{crop.crop_name}'",
            farm_id=crop.farm_id,
            crop_id=crop_id,
        )

        await self.repo.delete(crop)

    async def get_tasks(
        self, user_id: str, crop_id: str, filter_date: date | None = None
    ) -> TaskListResponse:
        """Get daily tasks for a crop."""
        await self._check_crop_ownership(user_id, crop_id)
        tasks = await self.repo.get_tasks_by_crop(crop_id, filter_date)
        task_responses = [DailyTaskResponse.model_validate(t) for t in tasks]
        completed = sum(1 for t in tasks if t.is_completed)
        return TaskListResponse(
            tasks=task_responses,
            total=len(tasks),
            completed_count=completed,
        )

    async def update_task(
        self, user_id: str, task_id: str, data: DailyTaskUpdate
    ) -> DailyTaskResponse:
        """Update a daily task (mark complete, add notes)."""
        update_data = data.model_dump(exclude_unset=True)
        task = await self.repo.update_task(task_id, **update_data)
        if not task:
            raise NotFoundException("Task", task_id)
        return DailyTaskResponse.model_validate(task)
