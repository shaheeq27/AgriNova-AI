"""
AgriNova AI — Chat Request / Response Schemas.

Phase 2: ``conversation_id`` for continuing threads.
Phase 3: ``farm_id`` for farm-contextual conversations.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message from the farmer.

    ``conversation_id``: omit to start a new conversation, provide to
    continue an existing one.

    ``farm_id``: optional farm to scope the conversation to.
    Once a conversation is locked to a farm, it cannot be changed.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="The farmer's question or message.",
        examples=["How often should I irrigate my tomato crop?"],
    )
    conversation_id: str | None = Field(
        default=None,
        description=(
            "Existing conversation ID to continue. "
            "Omit to start a new conversation."
        ),
    )
    farm_id: str | None = Field(
        default=None,
        description=(
            "Farm ID to scope this conversation to. "
            "Once set, the conversation is locked to this farm."
        ),
    )


class ChatResponse(BaseModel):
    """AI response returned to the farmer."""

    response: str = Field(
        ...,
        description="Aira's response text.",
    )
    conversation_id: str = Field(
        ...,
        description="Conversation identifier (UUID).",
    )
