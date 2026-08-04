"""
AgriNova AI — Authentication API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse, UserUpdate
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    service = AuthService(db)
    token = await service.register(data)
    return APIResponse.success(data=token.model_dump(), message="Account created successfully")


@router.post("/login", response_model=APIResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate and receive a JWT token."""
    service = AuthService(db)
    token = await service.login(data)
    return APIResponse.success(data=token.model_dump(), message="Login successful")


@router.get("/me", response_model=APIResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's profile."""
    service = AuthService(db)
    profile = await service.get_profile(current_user.id)
    return APIResponse.success(data=profile.model_dump())


@router.put("/me", response_model=APIResponse)
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    service = AuthService(db)
    update_data = data.model_dump(exclude_unset=True)
    profile = await service.update_profile(current_user.id, **update_data)
    return APIResponse.success(data=profile.model_dump(), message="Profile updated")
