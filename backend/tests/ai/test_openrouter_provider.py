import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from app.ai.providers.openrouter import OpenRouterProvider
from app.ai.providers.base import (
    AIMessage,
    AIUpstreamRateLimitException,
    AIConfigurationException,
    AIProviderException
)

def create_mock_response(status_code, json_data=None, text_data=""):
    resp = MagicMock()
    resp.status_code = status_code
    if json_data:
        resp.json.return_value = json_data
    else:
        resp.json.side_effect = Exception("Not JSON")
        resp.text = text_data
    return resp

@pytest.mark.asyncio
async def test_openrouter_provider_error_classification_rate_limit():
    provider = OpenRouterProvider(api_key="dummy_key", model_name="dummy-model")
    
    mock_post = AsyncMock()
    # 429 quota exhausted
    resp = create_mock_response(429, json_data={"error": {"message": "Rate limit exceeded"}})
    mock_post.side_effect = httpx.HTTPStatusError("429 Client Error", request=MagicMock(), response=resp)
    
    # Mock the context manager for httpx.AsyncClient
    mock_client = MagicMock()
    mock_client.post = mock_post
    mock_client.__aenter__.return_value = mock_client
    
    messages = [AIMessage(role="user", content="Test")]
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AIUpstreamRateLimitException):
            await provider.generate_response(messages)

@pytest.mark.asyncio
async def test_openrouter_provider_error_classification_auth():
    provider = OpenRouterProvider(api_key="dummy_key", model_name="dummy-model")
    
    mock_post = AsyncMock()
    # 403 authorization failure
    resp = create_mock_response(403, json_data={"error": {"message": "Permission Denied"}})
    mock_post.side_effect = httpx.HTTPStatusError("403 Client Error", request=MagicMock(), response=resp)
    
    mock_client = MagicMock()
    mock_client.post = mock_post
    mock_client.__aenter__.return_value = mock_client
    
    messages = [AIMessage(role="user", content="Test")]
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AIConfigurationException):
            await provider.generate_response(messages)

@pytest.mark.asyncio
async def test_openrouter_provider_error_classification_503():
    provider = OpenRouterProvider(api_key="dummy_key", model_name="dummy-model")
    
    mock_post = AsyncMock()
    # 503 Server error
    resp = create_mock_response(503, text_data="Service Unavailable")
    mock_post.side_effect = httpx.HTTPStatusError("503 Server Error", request=MagicMock(), response=resp)
    
    mock_client = MagicMock()
    mock_client.post = mock_post
    mock_client.__aenter__.return_value = mock_client
    
    messages = [AIMessage(role="user", content="Test")]
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AIProviderException):
            await provider.generate_response(messages)

@pytest.mark.asyncio
async def test_openrouter_provider_network_error():
    provider = OpenRouterProvider(api_key="dummy_key", model_name="dummy-model")
    
    mock_post = AsyncMock()
    mock_post.side_effect = httpx.TimeoutException("Connection timed out")
    
    mock_client = MagicMock()
    mock_client.post = mock_post
    mock_client.__aenter__.return_value = mock_client
    
    messages = [AIMessage(role="user", content="Test")]
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AIProviderException) as exc:
            await provider.generate_response(messages)
        assert "timed out" in str(exc.value).lower()
