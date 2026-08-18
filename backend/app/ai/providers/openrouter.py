import json
import logging
import httpx
from typing import AsyncGenerator

from app.ai.providers.base import (
    AIMessage,
    BaseAIProvider,
    AIProviderException,
    AIConfigurationException,
    AIUpstreamRateLimitException,
)

logger = logging.getLogger(__name__)


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter LLM provider using OpenAI-compatible API.

    Parameters:
        api_key: OpenRouter API key.
        model_name: OpenRouter model identifier.
    """

    def __init__(self, api_key: str, model_name: str):
        if not api_key or api_key == "your-openrouter-api-key-here":
            raise AIConfigurationException(
                "OPENROUTER_API_KEY is not set. Add a valid key to your .env file."
            )
        if not model_name:
            raise AIConfigurationException(
                "OPENROUTER_MODEL_NAME is not set. Add a valid model to your .env file."
            )

        self._api_key = api_key
        self._model_name = model_name
        self._base_url = "https://openrouter.ai/api/v1/chat/completions"
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/shaheeq27/AgriNova-AI", # OpenRouter expects this
            "X-Title": "AgriNova AI",
        }
        self._timeout = httpx.Timeout(60.0)

    def _prepare_messages(self, messages: list[AIMessage]) -> list[dict]:
        """Format AIMessages to OpenAI-compatible messages."""
        formatted_messages = []
        for msg in messages:
            # Map roles: system -> system, user -> user, assistant -> assistant
            role = msg.role
            # BaseAIProvider AIMessage uses "model" instead of "assistant"? Wait, base.py says "assistant".
            if role == "model":
                role = "assistant"
            
            formatted_messages.append({"role": role, "content": msg.content})
        return formatted_messages

    def _handle_http_error(self, exc: httpx.HTTPStatusError):
        """Normalize HTTP errors from httpx."""
        status_code = exc.response.status_code
        try:
            error_msg = exc.response.json()
        except Exception:
            error_msg = exc.response.text

        if status_code in (401, 403):
            logger.error("OpenRouter authentication error: %s - %s", status_code, error_msg)
            raise AIConfigurationException() from exc
        if status_code == 429:
            logger.warning("OpenRouter upstream rate limit: %s - %s", status_code, error_msg)
            raise AIUpstreamRateLimitException() from exc
        if status_code == 404:
            logger.error("OpenRouter model not found error: %s - %s", status_code, error_msg)
            raise AIConfigurationException("Configured AI model not found on OpenRouter.") from exc
        
        logger.error("OpenRouter provider error: %s - %s", status_code, error_msg)
        raise AIProviderException() from exc

    async def generate_response(self, messages: list[AIMessage]) -> str:
        """Send messages to OpenRouter and return the response text."""
        payload = {
            "model": self._model_name,
            "messages": self._prepare_messages(messages),
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    self._base_url, headers=self._headers, json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                
                if not data.get("choices") or not data["choices"][0].get("message", {}).get("content"):
                    logger.warning("OpenRouter returned an empty response.")
                    return (
                        "I apologize, but I wasn't able to generate a helpful response "
                        "for that question. Could you please rephrase it?"
                    )
                    
                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            logger.error("OpenRouter network error: %s", exc)
            raise AIProviderException("AI service request timed out or network error. Please try again.") from exc
        except Exception as exc:
            logger.error("Unexpected OpenRouter error: %s", exc, exc_info=True)
            raise AIProviderException() from exc

    async def generate_response_stream(self, messages: list[AIMessage]) -> AsyncGenerator[str, None]:
        """Send messages to OpenRouter and yield the response text in chunks."""
        payload = {
            "model": self._model_name,
            "messages": self._prepare_messages(messages),
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream(
                    "POST", self._base_url, headers=self._headers, json=payload
                ) as response:
                    if response.status_code != 200:
                        await response.aread()
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line:
                            continue
                        if line == "data: [DONE]":
                            break
                        if line.startswith("data: "):
                            data_str = line[6:]
                            try:
                                data = json.loads(data_str)
                                if data.get("choices"):
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                logger.warning("OpenRouter stream JSON decode error: %s", data_str)
                                continue

        except httpx.HTTPStatusError as exc:
            self._handle_http_error(exc)
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            logger.error("OpenRouter network error: %s", exc)
            raise AIProviderException("AI service request timed out or network error. Please try again.") from exc
        except Exception as exc:
            logger.error("Unexpected OpenRouter error: %s", exc, exc_info=True)
            raise AIProviderException() from exc
