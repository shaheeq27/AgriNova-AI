import pytest
from unittest.mock import AsyncMock, MagicMock

from google.genai import errors as genai_errors
from app.ai.providers.gemini import (
    GeminiProvider, 
    AIUpstreamRateLimitException, 
    AIConfigurationException
)
from app.ai.providers.base import AIMessage

@pytest.mark.asyncio
async def test_gemini_provider_error_classification_rate_limit():
    provider = GeminiProvider(api_key="dummy_key", model_name="gemini-3.5-flash")
    provider._client = MagicMock()
    mock_generate = AsyncMock()
    
    # 429 quota exhausted with the exact problematic string
    err_message = "429 RESOURCE_EXHAUSTED. Please retry in 17.819403421s."
    client_error = genai_errors.ClientError(429, {"error": {"message": err_message}})
    
    mock_generate.side_effect = client_error
    provider._client.aio.models.generate_content = mock_generate
    
    messages = [AIMessage(role="user", content="Test")]
    
    # Must raise AIUpstreamRateLimitException, NOT AIConfigurationException
    with pytest.raises(AIUpstreamRateLimitException):
        await provider.generate_response(messages)

@pytest.mark.asyncio
async def test_gemini_provider_error_classification_auth():
    provider = GeminiProvider(api_key="dummy_key", model_name="gemini-3.5-flash")
    provider._client = MagicMock()
    mock_generate = AsyncMock()
    
    # 403 authorization failure
    err_message = "403 Permission Denied"
    client_error = genai_errors.ClientError(403, {"error": {"message": err_message}})
    
    mock_generate.side_effect = client_error
    provider._client.aio.models.generate_content = mock_generate
    
    messages = [AIMessage(role="user", content="Test")]
    
    with pytest.raises(AIConfigurationException):
        await provider.generate_response(messages)

@pytest.mark.asyncio
async def test_gemini_provider_error_classification_fallback():
    provider = GeminiProvider(api_key="dummy_key", model_name="gemini-3.5-flash")
    provider._client = MagicMock()
    mock_generate = AsyncMock()
    
    # Missing structured code, but string indicates api key issue
    err_message = "API key not valid. Please pass a valid API key."
    # Simulate missing code by creating a generic exception and setting code manually
    client_error = genai_errors.ClientError(400, {"error": {"message": err_message}})
    client_error.code = None # Override to test fallback
    
    mock_generate.side_effect = client_error
    provider._client.aio.models.generate_content = mock_generate
    
    messages = [AIMessage(role="user", content="Test")]
    
    with pytest.raises(AIConfigurationException):
        await provider.generate_response(messages)
