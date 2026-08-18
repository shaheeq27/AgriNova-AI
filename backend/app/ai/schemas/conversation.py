"""
AgriNova AI — Conversation response schemas.

Pydantic models for conversation list, detail, and message responses.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """A single message within a conversation."""

    id: str
    role: str = Field(..., description="Message role: 'user' or 'assistant'.")
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Conversation summary for list views (no messages)."""

    id: str
    title: str | None = None
    farm_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetailResponse(BaseModel):
    """Full conversation with message history."""

    id: str
    title: str | None = None
    farm_id: str | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    """Wrapper for conversation list endpoint."""

    conversations: list[ConversationResponse]
    total: int
