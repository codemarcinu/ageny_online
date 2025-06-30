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
        "text": "Mock OCR text",
        "confidence": 0.95,
        "provider": "mock"
    }
    mock_provider.health_check.return_value = {"status": "healthy"}
    return mock_provider


@pytest.fixture
def mock_user_data():
    """Mock user data for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True
    }


@pytest.fixture
def mock_conversation_data():
    """Mock conversation data for testing."""
    return {
        "id": 1,
        "user_id": 1,
        "title": "Test conversation",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_message_data():
    """Mock message data for testing."""
    return {
        "id": 1,
        "conversation_id": 1,
        "role": "user",
        "content": "Test message",
        "timestamp": "2024-01-01T00:00:00Z",
        "tokens_used": 10,
        "cost": 0.001
    }


@pytest.fixture
def mock_ocr_data():
    """Mock OCR data for testing."""
    return {
        "id": 1,
        "user_id": 1,
        "text": "Extracted text",
        "confidence": 0.95,
        "provider": "mock",
        "cost": 0.001
    }


@pytest.fixture
def mock_cost_data():
    """Mock cost tracking data for testing."""
    return {
        "id": 1,
        "user_id": 1,
        "service": "llm",
        "provider": "mock",
        "tokens_used": 100,
        "cost": 0.01,
        "timestamp": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    mock_store = Mock()
    mock_store.add_documents.return_value = True
    mock_store.search.return_value = [
        {"id": "doc1", "score": 0.95, "text": "Sample document"}
    ]
    return mock_store


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "database_url": TEST_DATABASE_URL,
        "openai_api_key": "test-key",
        "mistral_api_key": "test-key",
        "azure_vision_key": "test-key",
        "google_vision_credentials_path": "test-path"
    }


@pytest.fixture(autouse=True)
def setup_test_environment(test_config):
    """Setup test environment."""
    # Don't override settings automatically - let tests set their own values
    pass


@pytest.fixture
def setup_providers():
    """Setup mock providers for testing."""
    # Mock provider factory methods
    provider_factory.get_available_providers = Mock(return_value=["openai", "mistral"])
    provider_factory.get_provider = Mock(return_value=mock_llm_provider())
    
    ocr_provider_factory.get_available_providers = Mock(return_value=["azure_vision", "google_vision"])
    ocr_provider_factory.get_provider = Mock(return_value=mock_ocr_provider())
