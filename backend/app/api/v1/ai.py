"""
AgriNova AI — AI Agronomist API Router (V3).

Endpoints:
    POST   /ai/chat                   Send a message to Aira.
    GET    /ai/conversations          List the user's conversations.
    GET    /ai/conversations/{id}     Get a conversation with messages.
    DELETE /ai/conversations/{id}     Soft-delete a conversation.

Authentication:
    All endpoints require a valid JWT bearer token via the existing
    ``get_current_user`` dependency.

Rate Limiting:
    The chat endpoint is protected by a per-user fixed-window limiter.
    Conversation CRUD endpoints are not rate-limited.

Streaming:
    Phase 2 uses normal JSON request/response.
    Phase 9 will add SSE streaming on a separate endpoint.
"""

import json
import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.rate_limiter import ai_rate_limiter
from app.ai.schemas.chat import ChatRequest, ChatResponse
from app.ai.schemas.conversation import (
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
)
from app.ai.services.ai_service import AIService
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Agronomist"])


# ── Chat ────────────────────────────────────────────────────────────────────


@router.post("/chat", response_model=APIResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to Aira, the AI Agronomist.

    Requires authentication.  Subject to per-user rate limiting.

    - **message**: The farmer's question (1–4000 characters).
    - **conversation_id**: Optional.  Omit to start a new conversation,
      provide to continue an existing one.

    Returns Aira's response and the ``conversation_id``.
    """
    # Per-user rate limit check
    await ai_rate_limiter.check(str(current_user.id))

    # Process the message
    service = AIService(db)
    result = await service.chat(str(current_user.id), request)

    return APIResponse.success(
        data=result.model_dump(),
        message="Aira has responded.",
    )


@router.post("/chat/stream")
async def chat_stream_endpoint(
    request: ChatRequest,
    fastapi_request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to Aira and stream the response via Server-Sent Events (SSE)."""
    # Rate limit check with IP for global backstop
    client_ip = fastapi_request.client.host if fastapi_request.client else None
    await ai_rate_limiter.check(str(current_user.id), ip_address=client_ip)

    service = AIService(db)

    async def sse_generator():
        try:
            async for payload in service.chat_stream(str(current_user.id), request):
                yield f"data: {json.dumps(payload)}\n\n"
        except Exception as e:
            logger.error("SSE streaming error: %s", e, exc_info=True)
            error_payload = {"type": "error", "message": "Aira could not complete the response. Please try again."}
            yield f"data: {json.dumps(error_payload)}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")


# ── Conversation CRUD ───────────────────────────────────────────────────────


@router.get("/conversations", response_model=APIResponse)
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the authenticated user's conversations (newest first)."""
    service = AIService(db)
    conversations, total = await service.get_conversations(str(current_user.id))

    data = ConversationListResponse(
        conversations=[
            ConversationResponse.model_validate(c) for c in conversations
        ],
        total=total,
    )

    return APIResponse.success(
        data=data.model_dump(),
        message="Conversations retrieved.",
    )


@router.get("/conversations/{conversation_id}", response_model=APIResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a conversation with its full message history.

    Returns 404 if the conversation does not exist or belongs to
    another user.
    """
    service = AIService(db)
    conversation = await service.get_conversation(
        str(current_user.id), conversation_id
    )

    data = ConversationDetailResponse.model_validate(conversation)

    return APIResponse.success(
        data=data.model_dump(),
        message="Conversation retrieved.",
    )


@router.delete("/conversations/{conversation_id}", response_model=APIResponse)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a conversation.

    Returns 404 if the conversation does not exist or belongs to
    another user.
    """
    service = AIService(db)
    await service.delete_conversation(str(current_user.id), conversation_id)

    return APIResponse.success(
        message="Conversation deleted.",
    )
