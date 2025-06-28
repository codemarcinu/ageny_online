"""
Test configuration for Ageny Online.
Zapewnia konfigurację testów z pełną separacją od my_assistant.
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator
from unittest.mock import Mock

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from backend.models.base import Base
from backend.database import get_async_session
from backend.core.llm_providers.provider_factory import provider_factory
from backend.core.ocr_providers.ocr_factory import ocr_provider_factory


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    echo=False
)

# Create test session factory
TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing."""
    mock_provider = Mock()
    mock_provider.chat.return_value = "Mock response"
    mock_provider.embed.return_value = [0.1, 0.2, 0.3]
    mock_provider.health_check.return_value = {"status": "healthy"}
    return mock_provider


@pytest.fixture
def mock_ocr_provider():
    """Mock OCR provider for testing."""
    mock_provider = Mock()
    mock_provider.extract_text.return_value = {
        "text": "Mock extracted text",
        "confidence": 0.95,
        "model_used": "mock-model",
        "tokens_used": 100,
        "cost": 0.001,
        "metadata": {"provider": "mock"}
    }
    mock_provider.extract_text_batch.return_value = [
        {
            "text": "Mock text 1",
            "confidence": 0.9,
            "image_index": 0,
            "metadata": {"provider": "mock"}
        },
        {
            "text": "Mock text 2", 
            "confidence": 0.9,
            "image_index": 1,
            "metadata": {"provider": "mock"}
        }
    ]
    mock_provider.health_check.return_value = {"status": "healthy"}
    return mock_provider


@pytest.fixture
def mock_user_data():
    """Mock user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }


@pytest.fixture
def mock_conversation_data():
    """Mock conversation data for testing."""
    return {
        "title": "Test Conversation",
        "session_id": "test-session-123",
        "agent_type": "general",
        "provider_used": "openai",
        "metadata": {"test": True}
    }


@pytest.fixture
def mock_message_data():
    """Mock message data for testing."""
    return {
        "conversation_id": 1,
        "role": "user",
        "content": "Hello, this is a test message",
        "provider_used": "openai",
        "model_used": "gpt-4",
        "tokens_used": 10,
        "cost": "0.001",
        "processing_time": "0.5s",
        "metadata": {"test": True}
    }


@pytest.fixture
def mock_ocr_data():
    """Mock OCR data for testing."""
    return {
        "provider": "mistral_vision",
        "model": "mistral-large-latest",
        "prompt": "Extract text from this image"
    }


@pytest.fixture
def mock_cost_data():
    """Mock cost data for testing."""
    return {
        "date": "2024-01-15",
        "provider": "openai",
        "service_type": "chat",
        "model_used": "gpt-4",
        "tokens_used": 100,
        "cost": "0.002",
        "request_count": 1,
        "metadata": {"test": True}
    } 