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


from app.core.rate_limit import auth_rate_limit

@router.post("/register", response_model=APIResponse, dependencies=[Depends(auth_rate_limit)])
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    service = AuthService(db)
    token = await service.register(data)
    return APIResponse.success(data=token.model_dump(), message="Account created successfully")


@router.post("/login", response_model=APIResponse, dependencies=[Depends(auth_rate_limit)])
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

from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest

@router.post("/forgot-password", response_model=APIResponse, dependencies=[Depends(auth_rate_limit)])
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Request a password reset link."""
    service = AuthService(db)
    await service.forgot_password(data.email)
    # Always return success to prevent email enumeration
    return APIResponse.success(message="If an account exists, a recovery link has been sent.")

@router.post("/reset-password", response_model=APIResponse)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password using a token."""
    service = AuthService(db)
    await service.reset_password(data.reset_id, data.token, data.new_password)
    return APIResponse.success(message="Password successfully updated")
