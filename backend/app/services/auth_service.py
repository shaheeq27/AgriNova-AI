"""
AgriNova AI — Authentication service.

Business logic for user registration and login.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import ConflictException, UnauthorizedException, AgriNovaException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.models.password_reset import PasswordReset
from app.repositories.user_repo import UserRepository
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from app.services.email_service import EmailService

import secrets
import string
from datetime import datetime, timezone
import os

class AuthService:
    """Authentication and user management business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)
        self.email_service = EmailService(db)

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

    async def forgot_password(self, email: str) -> None:
        """Handle forgot password request."""
        user = await self.repo.get_by_email(email)
        if not user or not user.is_active:
            # We silently return to avoid email enumeration
            return

        # Generate a secure token
        raw_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

        # We don't store raw_token, we store the hash
        hashed_token = hash_password(raw_token)

        reset_entry = PasswordReset(
            user_id=user.id,
            token_hash=hashed_token
        )
        self.db.add(reset_entry)
        await self.db.commit()
        await self.db.refresh(reset_entry)

        # Generate Recovery URL
        from app.core.config import settings
        frontend_url = settings.FRONTEND_URL.rstrip("/")
        recovery_url = f"{frontend_url}/reset-password?reset_id={reset_entry.id}&token={raw_token}"

        # Send email (using existing EmailService conceptually, or print to console)
        # Note: We bypass maybe_send_email preference checks for security emails
        provider = self.email_service._provider

        # We'll construct a simple email or print
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Password reset requested for user {user.id}. Delivery provider: {provider.provider_name}")

        # Optionally use the actual provider if it's not console
        if provider.provider_name != "console":
            try:
                from app.integrations.email import EmailMessage
                html_body = f"""
                <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>AgriNova AI</h2>
                    <h3>Reset Your Password</h3>
                    <p>Hello {user.full_name},</p>
                    <p>You recently requested to reset your password for your AgriNova AI account. Click the button below to reset it.</p>
                    <p><a href="{recovery_url}" style="display: inline-block; padding: 10px 20px; background-color: #2e7d32; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a></p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p><a href="{recovery_url}">{recovery_url}</a></p>
                    <p><strong>Note:</strong> This link will expire in 1 hour.</p>
                    <p>If you did not request a password reset, please ignore this email.</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #777;">&copy; AgriNova AI</p>
                </div>
                """
                msg = EmailMessage(
                    to_email=user.email,
                    to_name=user.full_name,
                    subject="AgriNova AI: Password Reset Request",
                    text_body=f"Hello {user.full_name},\n\nYou requested a password reset. Click the link below to reset your password:\n{recovery_url}\n\nNote: This link will expire in 1 hour.\n\nIf you did not request this, please ignore this email.",
                    html_body=html_body,
                    category="security"
                )
                result = await provider.execute_with_retry(message=msg)
                if not result.is_success:
                    logger.error(f"Brevo email failed: {result.error}")
            except Exception as e:
                logger.error(f"Failed to send real email: {e}")

    async def reset_password(self, reset_id: str, raw_token: str, new_password: str) -> None:
        """Process the password reset deterministically."""
        # Get specific token record
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.id == reset_id,
                PasswordReset.is_used == False
            )
        )
        target_reset = result.scalar_one_or_none()

        if not target_reset:
            raise AgriNovaException("Invalid or expired password reset token.", status_code=400)

        # Check expiration
        exp = target_reset.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp < datetime.now(timezone.utc):
            raise AgriNovaException("Invalid or expired password reset token.", status_code=400)

        # Verify hash
        if not verify_password(raw_token, target_reset.token_hash):
            raise AgriNovaException("Invalid or expired password reset token.", status_code=400)

        # Get user
        user = await self.repo.get_by_id(target_reset.user_id)
        if not user:
            raise AgriNovaException("User not found.", status_code=400)

        # Update password
        user.hashed_password = hash_password(new_password)
        target_reset.is_used = True

        await self.db.commit()
