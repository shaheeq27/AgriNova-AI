"""
AgriNova AI — Farm management service.

Business logic for farm CRUD with ownership validation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.farm import Farm
from app.repositories.farm_repo import FarmRepository
from app.schemas.farm import FarmCreate, FarmListResponse, FarmResponse, FarmUpdate


class FarmService:
    """Farm management business logic."""

    def __init__(self, db: AsyncSession):
        self.repo = FarmRepository(db)

    async def create_farm(self, user_id: str, data: FarmCreate) -> FarmResponse:
        """Create a new farm for the authenticated user.

        Args:
            user_id: Owning user's ID.
            data: Farm creation data.

        Returns:
            Created farm response.
        """
        farm = Farm(
            user_id=user_id,
            name=data.name,
            location_city=data.location_city,
            location_state=data.location_state,
            total_area_acres=data.total_area_acres,
            soil_type=data.soil_type,
            water_source=data.water_source,
            description=data.description,
        )
        farm = await self.repo.create(farm)
        return FarmResponse.model_validate(farm)

    async def list_farms(self, user_id: str) -> FarmListResponse:
        """List all active farms for the authenticated user."""
        farms = await self.repo.get_by_user_id(user_id)
        return FarmListResponse(
            farms=[FarmResponse.model_validate(f) for f in farms],
            total=len(farms),
        )

    async def get_farm(self, user_id: str, farm_id: str) -> FarmResponse:
        """Get a single farm by ID with ownership check.

        Raises:
            NotFoundException: If farm doesn't exist.
            ForbiddenException: If user doesn't own the farm.
        """
        farm = await self.repo.get_by_id(farm_id)
        if not farm:
            raise NotFoundException("Farm", farm_id)
        if farm.user_id != user_id:
            raise ForbiddenException("You do not have access to this farm")
        return FarmResponse.model_validate(farm)

    async def update_farm(self, user_id: str, farm_id: str, data: FarmUpdate) -> FarmResponse:
        """Update a farm with ownership check.

        Raises:
            NotFoundException: If farm doesn't exist.
            ForbiddenException: If user doesn't own the farm.
        """
        farm = await self.repo.get_by_id(farm_id)
        if not farm:
            raise NotFoundException("Farm", farm_id)
        if farm.user_id != user_id:
            raise ForbiddenException("You do not have access to this farm")

        update_data = data.model_dump(exclude_unset=True)
        farm = await self.repo.update(farm, **update_data)
        return FarmResponse.model_validate(farm)

    async def delete_farm(self, user_id: str, farm_id: str) -> None:
        """Soft-delete a farm with ownership check.

        Raises:
            NotFoundException: If farm doesn't exist.
            ForbiddenException: If user doesn't own the farm.
        """
        farm = await self.repo.get_by_id(farm_id)
        if not farm:
            raise NotFoundException("Farm", farm_id)
        if farm.user_id != user_id:
            raise ForbiddenException("You do not have access to this farm")
        await self.repo.soft_delete(farm)
