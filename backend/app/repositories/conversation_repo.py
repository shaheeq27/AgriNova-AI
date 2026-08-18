"""
AgriNova AI — Conversation repository.

Database operations for the Conversation and Message models.
All queries that fetch a conversation for a specific user scope by
both conversation_id AND user_id at the query level, so ownership
enforcement happens in the database, not in Python.
"""

from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message


class ConversationRepository:
    """Data access layer for Conversation and Message models."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Conversation CRUD ───────────────────────────────────────────────

    async def create(self, conversation: Conversation) -> Conversation:
        """Insert a new conversation."""
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def get_by_id_and_user_id(
        self, conversation_id: str, user_id: str
    ) -> Conversation | None:
        """Fetch a conversation scoped to the owning user.

        Returns None if the conversation does not exist, is inactive,
        or belongs to a different user.  This enforces ownership at the
        database query level.
        """
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> list[Conversation]:
        """List all active conversations for a user, newest first.

        Does NOT eagerly load messages — the list view only needs
        metadata (title, timestamps).
        """
        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.is_active == True,  # noqa: E712
            )
            .order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().all())

    async def count_by_user_id(self, user_id: str) -> int:
        """Count active conversations for a user."""
        result = await self.db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.user_id == user_id,
                Conversation.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one()

    async def update_title(self, conversation: Conversation, title: str) -> None:
        """Set the conversation title."""
        conversation.title = title
        await self.db.flush()

    async def touch(self, conversation: Conversation) -> None:
        """Update the conversation's updated_at timestamp."""
        conversation.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def soft_delete(self, conversation: Conversation) -> None:
        """Soft-delete a conversation by setting is_active = False."""
        conversation.is_active = False
        await self.db.flush()

    # ── Message operations ──────────────────────────────────────────────

    async def add_message(self, message: Message) -> Message:
        """Append a message to a conversation."""
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_messages(self, conversation_id: str) -> list[Message]:
        """Fetch all messages for a conversation, ordered chronologically."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())
