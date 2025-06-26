import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# from backend.config import settings  # Usunięto, nie jest już potrzebny
from backend.core.llm_providers.provider_factory import llm_factory, ProviderType, ProviderConfig
from backend.core.ocr_providers.ocr_factory import ocr_factory, OCRProviderType, OCRProviderConfig

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "text": "This is a test response from OpenAI",
        "model": "gpt-4o-mini",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "cost": {
            "input_cost": 0.0015,
            "output_cost": 0.012,
            "total_cost": 0.0135
        },
        "finish_reason": "stop"
    }

@pytest.fixture
def mock_mistral_response():
    """Mock Mistral API response."""
    return {
        "text": "This is a test response from Mistral",
        "model": "mistral-small-latest",
        "usage": {
            "prompt_tokens": 8,
            "completion_tokens": 15,
            "total_tokens": 23
        },
        "cost": {
            "input_cost": 0.00112,
            "output_cost": 0.0063,
            "total_cost": 0.00742
        },
        "finish_reason": "stop"
    }

@pytest.fixture
def mock_ocr_response():
    """Mock OCR API response."""
    return {
        "text": "Sample receipt text extracted from image",
        "confidence": 0.95,
        "language": "en",
        "bounding_boxes": [
            {
                "text": "Sample receipt",
                "confidence": 0.95,
                "bbox": [10, 10, 100, 30]
            }
        ],
        "provider": "azure_vision",
        "cost": 0.0015
    }

@pytest.fixture
def mock_vector_search_response():
    """Mock vector search response."""
    return {
        "matches": [
            {
                "id": "doc1",
                "score": 0.95,
                "text": "Sample document text",
                "metadata": {"category": "sample"}
            },
            {
                "id": "doc2", 
                "score": 0.85,
                "text": "Another document",
                "metadata": {"category": "sample"}
            }
        ],
        "provider": "pinecone",
        "cost": 0.0001
    }

@pytest.fixture
def sample_messages():
    """Sample chat messages for testing."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]

@pytest.fixture
def sample_documents():
    """Sample documents for vector store testing."""
    return [
        {
            "id": "doc1",
            "text": "This is a sample document about AI and machine learning.",
            "metadata": {"category": "technology", "author": "test"}
        },
        {
            "id": "doc2",
            "text": "Another document about data science and analytics.",
            "metadata": {"category": "technology", "author": "test"}
        }
    ]

@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing."""
    provider = Mock()
    provider.chat = AsyncMock(return_value={
        "text": "Mock response",
        "model": "test-model",
        "usage": {"total_tokens": 10},
        "cost": {"total_cost": 0.01}
    })
    provider.embed = AsyncMock(return_value={
        "embeddings": [[0.1, 0.2, 0.3]],
        "cost": 0.001
    })
    provider.get_available_models = Mock(return_value=["test-model"])
    return provider

@pytest.fixture
def mock_ocr_provider():
    """Mock OCR provider for testing."""
    provider = Mock()
    provider.extract_text = AsyncMock(return_value={
        "text": "Mock OCR text",
        "confidence": 0.9,
        "cost": 0.0015
    })
    provider.get_supported_languages = Mock(return_value=["en", "pl"])
    return provider

@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    store = Mock()
    store.upsert_vectors = AsyncMock(return_value={
        "upserted_count": 2,
        "cost": 0.0002
    })
    store.query_vectors = AsyncMock(return_value={
        "matches": [
            {"id": "doc1", "score": 0.9, "metadata": {"text": "test"}}
        ],
        "cost": 0.0001
    })
    return store

@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "openai_api_key": "test-openai-key",
        "mistral_api_key": "test-mistral-key",
        "azure_vision_key": "test-azure-key",
        "azure_vision_endpoint": "https://test.cognitiveservices.azure.com/",
        "pinecone_api_key": "test-pinecone-key",
        "pinecone_environment": "test-env"
    }

@pytest.fixture(autouse=True)
def setup_test_environment(test_config):
    """Setup test environment with mock API keys."""
    # Set test environment variables
    os.environ["OPENAI_API_KEY"] = test_config["openai_api_key"]
    os.environ["MISTRAL_API_KEY"] = test_config["mistral_api_key"]
    os.environ["AZURE_VISION_KEY"] = test_config["azure_vision_key"]
    os.environ["AZURE_VISION_ENDPOINT"] = test_config["azure_vision_endpoint"]
    os.environ["PINECONE_API_KEY"] = test_config["pinecone_api_key"]
    os.environ["PINECONE_ENVIRONMENT"] = test_config["pinecone_environment"]
    
    yield
    
    # Cleanup
    for key in test_config.keys():
        if key in os.environ:
            del os.environ[key]

@pytest.fixture
def setup_providers():
    """Setup test providers."""
    # Setup LLM providers
    llm_factory.register_provider(
        ProviderType.OPENAI,
        ProviderConfig(
            api_key="test-openai-key",
            priority=1
        )
    )
    
    llm_factory.register_provider(
        ProviderType.MISTRAL,
        ProviderConfig(
            api_key="test-mistral-key",
            priority=2
        )
    )
    
    # Setup OCR providers
    ocr_factory.register_provider(
        OCRProviderType.AZURE_VISION,
        OCRProviderConfig(
            azure_key="test-azure-key",
            azure_endpoint="https://test.cognitiveservices.azure.com/",
            priority=1
        )
    )
    
    yield
    
    # Cleanup
    llm_factory._configs.clear()
    llm_factory._instances.clear()
    ocr_factory._configs.clear()
    ocr_factory._instances.clear() 