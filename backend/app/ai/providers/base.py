"""
AgriNova AI — Base AI Provider.

Abstract interface for all LLM providers. Any new provider (OpenAI, Anthropic,
local models) must implement this contract so the rest of the AI module stays
provider-agnostic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.exceptions import AgriNovaException

class AIProviderException(AgriNovaException):
    """Upstream AI provider failed (timeout, unexpected error, etc.)."""
    def __init__(self, message: str = "AI service is temporarily unavailable. Please try again later."):
        super().__init__(message=message, status_code=503)

class AIConfigurationException(AgriNovaException):
    """AI provider is not configured correctly (missing/invalid API key)."""
    def __init__(self, message: str = "AI service is not configured. Please contact support."):
        super().__init__(message=message, status_code=503)

class AIUpstreamRateLimitException(AgriNovaException):
    """Upstream provider's own rate-limit was hit."""
    def __init__(self, message: str = "AI service is busy. Please try again in a moment."):
        super().__init__(message=message, status_code=503)

@dataclass
class AIMessage:
    """A single message in a conversation sent to the LLM.

    Attributes:
        role: One of "system", "user", or "assistant".
        content: The text content of the message.
    """

    role: str  # "system" | "user" | "assistant"
    content: str


class BaseAIProvider(ABC):
    """Abstract base class that every LLM provider must implement.

    The provider is responsible only for communicating with the upstream
    LLM API.  It must NOT contain AgriNova domain logic — that belongs
    in ``AIService``.
    """

    @abstractmethod
    async def generate_response(self, messages: list[AIMessage]) -> str:
        """Send a list of messages to the LLM and return the text response.

        Args:
            messages: Ordered conversation messages (system prompt first).

        Returns:
            The assistant's reply as a plain string.

        Raises:
            app.core.exceptions.AgriNovaException subclasses for all
            provider-level failures (see ``gemini.py`` for the concrete
            error-normalisation logic).
        """
        ...

    @abstractmethod
    async def generate_response_stream(self, messages: list[AIMessage]):
        """Send a list of messages to the LLM and yield the text response in chunks.
        
        Args:
            messages: Ordered conversation messages (system prompt first).

        Yields:
            str: Chunks of the assistant's reply.

        Raises:
            app.core.exceptions.AgriNovaException subclasses for all
            provider-level failures.
        """
        ...
