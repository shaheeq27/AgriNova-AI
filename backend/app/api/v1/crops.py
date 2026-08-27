"""
AgriNova AI — Crops API routes.

Crop recommendation, planting, lifecycle management, timeline, and daily tasks.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.crop import (
    CropCreate,
    CropRecommendationRequest,
    CropUpdate,
    DailyTaskUpdate,
)
from app.services.crop_service import CropService
from app.services import crop_recommendation_service, timeline_service
from app.ai.services.historical_insights_service import HistoricalInsightsService

router = APIRouter(prefix="/crops", tags=["Crops"])


# ── Recommendation ──


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.repositories.user_repo import UserRepository
from fastapi import HTTPException, status, Security

security_optional = HTTPBearer(auto_error=False)

async def get_optional_user(db: AsyncSession, credentials: HTTPAuthorizationCredentials | None) -> User | None:
    if not credentials or not hasattr(credentials, 'credentials'):
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    repo = UserRepository(db)
    user = await repo.get_by_id(payload["sub"])
    if not user or not user.is_active:
        return None
    return user

@router.post("/recommend")
async def recommend_crops(
    data: CropRecommendationRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(security_optional),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-powered crop recommendations based on environmental conditions."""
    historical_insights = None
    if data.farm_id:
        user = await get_optional_user(db, credentials)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Must be logged in to use farm context")

        from app.services.farm_service import FarmService
        farm_service = FarmService(db)
        await farm_service.get_farm(user.id, data.farm_id) # validates ownership

        insights_service = HistoricalInsightsService()
        historical_insights = await insights_service.compute_insights_context(db, data.farm_id)

    recommendations = await crop_recommendation_service.recommend_crops(
        db=db,
        temperature=data.temperature,
        humidity=data.humidity,
        rainfall=data.rainfall,
        soil_type=data.soil_type,
        n=data.n,
        p=data.p,
        k=data.k,
        ph=data.ph,
        historical_insights=historical_insights,
    )
    return APIResponse.success(
        data={
            "recommendations": recommendations,
            "input_conditions": data.model_dump(),
        },
        message=f"Found {len(recommendations)} crop recommendations",
    )


# ── Crop CRUD ──


@router.post("/plant")
async def plant_crop(
    data: CropCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Plant a crop on a farm — auto-generates timeline and daily tasks."""
    service = CropService(db)
    crop = await service.create_crop(user.id, data)
    return APIResponse.success(data=crop.model_dump(mode="json"), message="Crop planted successfully")


@router.get("/farm/{farm_id}")
async def list_farm_crops(
    farm_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all crops for a specific farm."""
    service = CropService(db)
    result = await service.list_crops(user.id, farm_id)
    return APIResponse.success(data=result.model_dump(mode="json"))


@router.get("/{crop_id}")
async def get_crop(
    crop_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get detailed crop information."""
    service = CropService(db)
    crop = await service.get_crop(user.id, crop_id)
    return APIResponse.success(data=crop.model_dump(mode="json"))


@router.put("/{crop_id}")
async def update_crop(
    crop_id: str,
    data: CropUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update crop details."""
    service = CropService(db)
    crop = await service.update_crop(user.id, crop_id, data)
    return APIResponse.success(data=crop.model_dump(mode="json"), message="Crop updated")


@router.delete("/{crop_id}")
async def delete_crop(
    crop_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a crop and its timeline."""
    service = CropService(db)
    await service.delete_crop(user.id, crop_id)
    return APIResponse.success(message="Crop deleted")


# ── Timeline ──


@router.get("/{crop_id}/timeline")
async def get_crop_timeline(
    crop_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the full timeline for a crop."""
    # Verify ownership
    service = CropService(db)
    await service.get_crop(user.id, crop_id)

    timeline = await timeline_service.get_timeline(db, crop_id)
    return APIResponse.success(data=timeline.model_dump(mode="json"))


# ── Daily Tasks ──


@router.get("/{crop_id}/tasks")
async def get_crop_tasks(
    crop_id: str,
    filter_date: date | None = Query(None, alias="date"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get daily tasks for a crop, optionally filtered by date."""
    service = CropService(db)
    result = await service.get_tasks(user.id, crop_id, filter_date)
    return APIResponse.success(data=result.model_dump(mode="json"))


@router.put("/tasks/{task_id}")
async def update_task(
    task_id: str,
    data: DailyTaskUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mark a task as complete/incomplete or add notes."""
    service = CropService(db)
    task = await service.update_task(user.id, task_id, data)
    return APIResponse.success(data=task.model_dump(mode="json"), message="Task updated")
