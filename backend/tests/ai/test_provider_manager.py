import pytest
from unittest.mock import AsyncMock, MagicMock

from app.ai.providers.manager import AIProviderManager
from app.ai.providers.base import (
    AIMessage,
    BaseAIProvider,
    AIUpstreamRateLimitException,
    AIConfigurationException,
    AIProviderException
)

class MockProvider(BaseAIProvider):
    def __init__(self, name="mock"):
        self.name = name
        self.generate_response_mock = AsyncMock()
        self.generate_response_stream_mock = MagicMock()
        
    async def generate_response(self, messages):
        return await self.generate_response_mock(messages)
        
    async def generate_response_stream(self, messages):
        # iterate over the returned async generator directly
        async for chunk in self.generate_response_stream_mock(messages):
            yield chunk

@pytest.fixture
def gemini():
    return MockProvider("gemini")

@pytest.fixture
def openrouter():
    return MockProvider("openrouter")

@pytest.fixture
def manager(gemini, openrouter):
    return AIProviderManager([gemini, openrouter])

@pytest.mark.asyncio
async def test_gemini_success(manager, gemini, openrouter):
    gemini.generate_response_mock.return_value = "Gemini Response"
    
    messages = [AIMessage(role="user", content="Test")]
    response = await manager.generate_response(messages)
    
    assert response == "Gemini Response"
    gemini.generate_response_mock.assert_called_once()
    openrouter.generate_response_mock.assert_not_called()

@pytest.mark.asyncio
async def test_gemini_rate_limit(manager, gemini, openrouter):
    gemini.generate_response_mock.side_effect = AIUpstreamRateLimitException()
    openrouter.generate_response_mock.return_value = "OpenRouter Response"
    
    messages = [AIMessage(role="user", content="Test")]
    response = await manager.generate_response(messages)
    
    assert response == "OpenRouter Response"
    gemini.generate_response_mock.assert_called_once()
    openrouter.generate_response_mock.assert_called_once()

@pytest.mark.asyncio
async def test_gemini_503(manager, gemini, openrouter):
    gemini.generate_response_mock.side_effect = AIProviderException()
    openrouter.generate_response_mock.return_value = "OpenRouter Response"
    
    messages = [AIMessage(role="user", content="Test")]
    response = await manager.generate_response(messages)
    
    assert response == "OpenRouter Response"
    gemini.generate_response_mock.assert_called_once()
    openrouter.generate_response_mock.assert_called_once()

@pytest.mark.asyncio
async def test_gemini_timeout(manager, gemini, openrouter):
    gemini.generate_response_mock.side_effect = AIProviderException()
    openrouter.generate_response_mock.return_value = "OpenRouter Response"
    
    messages = [AIMessage(role="user", content="Test")]
    response = await manager.generate_response(messages)
    
    assert response == "OpenRouter Response"
    gemini.generate_response_mock.assert_called_once()
    openrouter.generate_response_mock.assert_called_once()

@pytest.mark.asyncio
async def test_gemini_auth_failure(manager, gemini, openrouter):
    gemini.generate_response_mock.side_effect = AIConfigurationException()
    
    messages = [AIMessage(role="user", content="Test")]
    with pytest.raises(AIConfigurationException):
        await manager.generate_response(messages)
        
    gemini.generate_response_mock.assert_called_once()
    openrouter.generate_response_mock.assert_not_called()

@pytest.mark.asyncio
async def test_both_providers_fail(manager, gemini, openrouter):
    gemini.generate_response_mock.side_effect = AIUpstreamRateLimitException()
    openrouter.generate_response_mock.side_effect = AIProviderException("Final failure")
    
    messages = [AIMessage(role="user", content="Test")]
    with pytest.raises(AIProviderException) as exc:
        await manager.generate_response(messages)
        
    assert "Final failure" in str(exc.value)
    gemini.generate_response_mock.assert_called_once()
    openrouter.generate_response_mock.assert_called_once()

@pytest.mark.asyncio
async def test_streaming_gemini_success(manager, gemini, openrouter):
    async def mock_stream(messages):
        yield "Chunk 1 "
        yield "Chunk 2"
        
    gemini.generate_response_stream_mock.side_effect = mock_stream
    
    messages = [AIMessage(role="user", content="Test")]
    
    chunks = []
    async for chunk in manager.generate_response_stream(messages):
        chunks.append(chunk)
        
    assert chunks == ["Chunk 1 ", "Chunk 2"]
    gemini.generate_response_stream_mock.assert_called_once()
    openrouter.generate_response_stream_mock.assert_not_called()

@pytest.mark.asyncio
async def test_streaming_gemini_fails_before_first_chunk(manager, gemini, openrouter):
    async def mock_gemini_stream(messages):
        raise AIUpstreamRateLimitException()
        yield "" # to make it an async generator
        
    async def mock_openrouter_stream(messages):
        yield "OR Chunk 1"
        
    gemini.generate_response_stream_mock.side_effect = mock_gemini_stream
    openrouter.generate_response_stream_mock.side_effect = mock_openrouter_stream
    
    messages = [AIMessage(role="user", content="Test")]
    
    chunks = []
    async for chunk in manager.generate_response_stream(messages):
        chunks.append(chunk)
        
    assert chunks == ["OR Chunk 1"]
    gemini.generate_response_stream_mock.assert_called_once()
    openrouter.generate_response_stream_mock.assert_called_once()

@pytest.mark.asyncio
async def test_streaming_gemini_fails_after_chunks(manager, gemini, openrouter):
    async def mock_gemini_stream(messages):
        yield "Gemini Chunk 1"
        raise AIUpstreamRateLimitException()
        
    gemini.generate_response_stream_mock.side_effect = mock_gemini_stream
    
    messages = [AIMessage(role="user", content="Test")]
    
    chunks = []
    with pytest.raises(AIUpstreamRateLimitException):
        async for chunk in manager.generate_response_stream(messages):
            chunks.append(chunk)
            
    assert chunks == ["Gemini Chunk 1"]
    gemini.generate_response_stream_mock.assert_called_once()
    # OpenRouter should not be called because chunks were already emitted
    openrouter.generate_response_stream_mock.assert_not_called()
