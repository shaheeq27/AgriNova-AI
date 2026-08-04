"""
AgriNova AI — Farm management API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.farm import FarmCreate, FarmUpdate
from app.services.farm_service import FarmService

router = APIRouter(prefix="/farms", tags=["Farm Management"])


@router.post("", response_model=APIResponse)
async def create_farm(
    data: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new farm."""
    service = FarmService(db)
    farm = await service.create_farm(current_user.id, data)
    return APIResponse.success(data=farm.model_dump(), message="Farm created successfully")


@router.get("", response_model=APIResponse)
async def list_farms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all farms for the current user."""
    service = FarmService(db)
    result = await service.list_farms(current_user.id)
    return APIResponse.success(data=result.model_dump())


@router.get("/{farm_id}", response_model=APIResponse)
async def get_farm(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific farm by ID."""
    service = FarmService(db)
    farm = await service.get_farm(current_user.id, farm_id)
    return APIResponse.success(data=farm.model_dump())


@router.put("/{farm_id}", response_model=APIResponse)
async def update_farm(
    farm_id: str,
    data: FarmUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a farm."""
    service = FarmService(db)
    farm = await service.update_farm(current_user.id, farm_id, data)
    return APIResponse.success(data=farm.model_dump(), message="Farm updated successfully")


@router.delete("/{farm_id}", response_model=APIResponse)
async def delete_farm(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a farm."""
    service = FarmService(db)
    await service.delete_farm(current_user.id, farm_id)
    return APIResponse.success(message="Farm deleted successfully")
