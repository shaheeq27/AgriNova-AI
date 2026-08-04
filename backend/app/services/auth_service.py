"""
AgriNova AI — Authentication service.

Business logic for user registration and login.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse


class AuthService:
    """Authentication and user management business logic."""

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, data: UserCreate) -> Token:
        """Register a new user account.

        Args:
            data: Registration form data.

        Returns:
            JWT token with user info.

        Raises:
            ConflictException: If email is already registered.
        """
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ConflictException("An account with this email already exists")

        user = User(
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
        )
        user = await self.repo.create(user)

        access_token = create_access_token(subject=user.id)
        return Token(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )

    async def login(self, data: UserLogin) -> Token:
        """Authenticate a user and issue a JWT token.

        Args:
            data: Login credentials.

        Returns:
            JWT token with user info.

        Raises:
            UnauthorizedException: If credentials are invalid.
        """
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        access_token = create_access_token(subject=user.id)
        return Token(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )

    async def get_profile(self, user_id: str) -> UserResponse:
        """Get user profile by ID.

        Raises:
            UnauthorizedException: If user not found.
        """
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")
        return UserResponse.model_validate(user)

    async def update_profile(self, user_id: str, **kwargs) -> UserResponse:
        """Update user profile fields.

        Raises:
            UnauthorizedException: If user not found.
        """
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")
        user = await self.repo.update(user, **kwargs)
        return UserResponse.model_validate(user)
