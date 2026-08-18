import logging
from typing import AsyncGenerator

from app.ai.providers.base import (
    AIMessage,
    BaseAIProvider,
    AIProviderException,
    AIConfigurationException,
    AIUpstreamRateLimitException,
)

logger = logging.getLogger(__name__)


class AIProviderManager(BaseAIProvider):
    """Manages ordered LLM providers with automatic fallback for recoverable errors."""

    def __init__(self, providers: list[BaseAIProvider]):
        if not providers:
            raise ValueError("AIProviderManager requires at least one provider.")
        self.providers = providers

    def _get_provider_name(self, provider: BaseAIProvider) -> str:
        name = provider.__class__.__name__.lower()
        if name.endswith("provider"):
            return name[:-8]
        return name

    async def generate_response(self, messages: list[AIMessage]) -> str:
        """Try providers in order until one succeeds or a non-recoverable error occurs."""
        last_exception = None

        for i, provider in enumerate(self.providers):
            provider_name = self._get_provider_name(provider)
            logger.info("Aira provider attempt | provider=%s", provider_name)

            try:
                response = await provider.generate_response(messages)
                logger.info("Aira provider success | provider=%s", provider_name)
                return response
            
            except (AIUpstreamRateLimitException, AIProviderException) as exc:
                last_exception = exc
                if i < len(self.providers) - 1:
                    next_provider_name = self._get_provider_name(self.providers[i + 1])
                    reason = "rate_limit" if isinstance(exc, AIUpstreamRateLimitException) else "provider_error"
                    logger.warning(
                        "Aira provider fallback | from=%s | to=%s | reason=%s",
                        provider_name,
                        next_provider_name,
                        reason,
                    )
                else:
                    logger.error("Aira provider failure | provider=%s | all providers failed", provider_name)
                    
            except AIConfigurationException as exc:
                # Non-recoverable error. Do not fallback.
                logger.error("Aira provider failure | provider=%s | configuration error", provider_name)
                raise exc

        # If we got here, all providers failed with recoverable errors.
        if last_exception:
            raise last_exception
        
        raise AIProviderException("All AI providers failed.")

    async def generate_response_stream(self, messages: list[AIMessage]) -> AsyncGenerator[str, None]:
        """Try providers in order for streaming. 
        
        Fallback only happens if the primary provider fails *before* yielding any content.
        Once content has been yielded, errors are propagated directly (no silent restart).
        """
        last_exception = None

        for i, provider in enumerate(self.providers):
            provider_name = self._get_provider_name(provider)
            logger.info("Aira provider attempt | provider=%s (stream)", provider_name)
            
            content_yielded = False

            try:
                async for chunk in provider.generate_response_stream(messages):
                    content_yielded = True
                    yield chunk
                    
                logger.info("Aira provider success | provider=%s (stream)", provider_name)
                return  # Stream completed successfully

            except (AIUpstreamRateLimitException, AIProviderException) as exc:
                last_exception = exc
                
                if content_yielded:
                    # We cannot fallback because we already sent chunks to the client.
                    # Propagating error to API layer.
                    logger.error(
                        "Aira provider stream interrupted | provider=%s | Cannot fallback mid-stream", 
                        provider_name
                    )
                    raise exc
                
                if i < len(self.providers) - 1:
                    next_provider_name = self._get_provider_name(self.providers[i + 1])
                    reason = "rate_limit" if isinstance(exc, AIUpstreamRateLimitException) else "provider_error"
                    logger.warning(
                        "Aira provider fallback | from=%s | to=%s | reason=%s (stream)",
                        provider_name,
                        next_provider_name,
                        reason,
                    )
                else:
                    logger.error("Aira provider failure | provider=%s | all providers failed (stream)", provider_name)
                    
            except AIConfigurationException as exc:
                logger.error("Aira provider failure | provider=%s | configuration error (stream)", provider_name)
                raise exc

        if last_exception:
            raise last_exception
            
        raise AIProviderException("All AI providers failed.")
