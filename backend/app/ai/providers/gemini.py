"""
AgriNova AI — Google Gemini Provider.

Concrete ``BaseAIProvider`` implementation that calls the Google Gemini API
via the ``google-genai`` SDK.  All upstream errors are normalized into safe
AgriNova exceptions so that no raw provider tracebacks leak to the client.
"""

import logging

from google import genai
from google.genai import types as genai_types
from google.genai import errors as genai_errors

from app.ai.providers.base import (
    AIMessage, 
    BaseAIProvider,
    AIProviderException,
    AIConfigurationException,
    AIUpstreamRateLimitException
)
from app.core.exceptions import AgriNovaException

logger = logging.getLogger(__name__)


# ── Gemini provider ─────────────────────────────────────────────────────────

class GeminiProvider(BaseAIProvider):
    """Google Gemini LLM provider.

    Parameters:
        api_key: Gemini API key (from ``settings.GEMINI_API_KEY``).
        model_name: Model identifier (default ``gemini-2.0-flash``).
    """

    def __init__(self, api_key: str, model_name: str = "gemini-3.5-flash"):
        if not api_key or api_key == "your-gemini-api-key-here":
            raise AIConfigurationException(
                "GEMINI_API_KEY is not set. Add a valid key to your .env file."
            )
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name

    # ── Public interface ────────────────────────────────────────────────────

    async def generate_response(self, messages: list[AIMessage]) -> str:
        """Send messages to Gemini and return the response text.

        Separates the system instruction from conversation messages, calls
        the Gemini API, and normalizes every category of upstream failure.
        """
        system_instruction, contents = self._prepare_messages(messages)

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model_name,
                contents=contents,
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
            )

            # Extract text — handle blocked / empty responses
            if not response.text:
                logger.warning("Gemini returned an empty response.")
                return (
                    "I apologize, but I wasn't able to generate a helpful response "
                    "for that question. Could you please rephrase it?"
                )

            return response.text

        except genai_errors.ClientError as exc:
            # 400-level errors: bad request, auth failure, quota
            status_code = getattr(exc, "code", None)

            if status_code in (401, 403):
                logger.error("Gemini authentication error: %s", exc)
                raise AIConfigurationException() from exc
            if status_code == 429:
                logger.warning("Gemini upstream rate limit: %s", exc)
                raise AIUpstreamRateLimitException() from exc
            if status_code == 404:
                logger.error("Gemini model not found error: %s", exc)
                raise AIConfigurationException(f"Configured AI model not found.") from exc
                
            # Fallback for unexpected structured formats
            error_msg = str(exc).lower()
            if "api key" in error_msg or "unauthorized" in error_msg:
                logger.error("Gemini authentication error: %s", exc)
                raise AIConfigurationException() from exc
            if "quota" in error_msg or "rate limit" in error_msg:
                logger.warning("Gemini upstream rate limit: %s", exc)
                raise AIUpstreamRateLimitException() from exc
                
            logger.error("Gemini client error: %s", exc)
            raise AIProviderException() from exc

        except genai_errors.ServerError as exc:
            logger.error("Gemini server error: %s", exc)
            raise AIProviderException() from exc

        except TimeoutError as exc:
            logger.error("Gemini request timed out: %s", exc)
            raise AIProviderException(
                "AI service request timed out. Please try again."
            ) from exc

        except Exception as exc:
            # Catch-all — never leak raw provider exceptions
            logger.error("Unexpected Gemini error: %s", exc, exc_info=True)
            raise AIProviderException() from exc

    async def generate_response_stream(self, messages: list[AIMessage]):
        """Send messages to Gemini and yield the response text in chunks."""
        system_instruction, contents = self._prepare_messages(messages)

        try:
            response_stream = await self._client.aio.models.generate_content_stream(
                model=self._model_name,
                contents=contents,
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
            )

            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        except genai_errors.ClientError as exc:
            status_code = getattr(exc, "code", None)

            if status_code in (401, 403):
                logger.error("Gemini authentication error: %s", exc)
                raise AIConfigurationException() from exc
            if status_code == 429:
                logger.warning("Gemini upstream rate limit: %s", exc)
                raise AIUpstreamRateLimitException() from exc
            if status_code == 404:
                logger.error("Gemini model not found error: %s", exc)
                raise AIConfigurationException(f"Configured AI model not found.") from exc
                
            error_msg = str(exc).lower()
            if "api key" in error_msg or "unauthorized" in error_msg:
                logger.error("Gemini authentication error: %s", exc)
                raise AIConfigurationException() from exc
            if "quota" in error_msg or "rate limit" in error_msg:
                logger.warning("Gemini upstream rate limit: %s", exc)
                raise AIUpstreamRateLimitException() from exc
                
            logger.error("Gemini client error: %s", exc)
            raise AIProviderException() from exc
        except genai_errors.ServerError as exc:
            logger.error("Gemini server error: %s", exc)
            raise AIProviderException() from exc
        except TimeoutError as exc:
            logger.error("Gemini request timed out: %s", exc)
            raise AIProviderException("AI service request timed out. Please try again.") from exc
        except Exception as exc:
            logger.error("Unexpected Gemini error: %s", exc, exc_info=True)
            raise AIProviderException() from exc

    # ── Private helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _prepare_messages(
        messages: list[AIMessage],
    ) -> tuple[str | None, list[genai_types.Content]]:
        """Split messages into a system instruction and Content objects.

        Gemini expects the system instruction separately from conversation
        turns.  This helper extracts the first ``system`` message and
        converts the remaining ``user``/``assistant`` messages into the
        ``Content`` format the SDK expects.
        """
        system_instruction: str | None = None
        contents: list[genai_types.Content] = []

        for msg in messages:
            if msg.role == "system":
                # Concatenate in case there are multiple system messages
                if system_instruction is None:
                    system_instruction = msg.content
                else:
                    system_instruction += "\n\n" + msg.content
            else:
                role = "user" if msg.role == "user" else "model"
                contents.append(
                    genai_types.Content(
                        role=role,
                        parts=[genai_types.Part(text=msg.content)],
                    )
                )

        return system_instruction, contents
