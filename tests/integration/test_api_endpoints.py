import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.api.main import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

class TestHealthEndpoints:
    """Test health and status endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Ageny Online API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "endpoints" in data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "llm_providers" in data
        assert "ocr_providers" in data
        assert "vector_stores" in data
        assert "timestamp" in data
    
    def test_providers_endpoint(self, client):
        """Test providers endpoint."""
        response = client.get("/api/v1/providers")
        
        assert response.status_code == 200
        data = response.json()
        assert "llm_providers" in data
        assert "ocr_providers" in data
        assert "vector_stores" in data
        assert "priorities" in data

class TestChatEndpoints:
    """Test chat completion endpoints."""
    
    @patch('backend.core.llm_providers.provider_factory.llm_factory')
    def test_chat_completion(self, mock_factory, client):
        """Test chat completion endpoint."""
        # Mock the factory response
        mock_factory.chat_with_fallback.return_value = {
            "text": "Hello! I'm doing well, thank you for asking.",
            "model": "gpt-4o-mini",
            "provider": "openai",
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
            "finish_reason": "stop",
            "response_time": 1.5
        }
        
        request_data = {
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "model": "gpt-4o-mini",
            "temperature": 0.7
        }
        
        response = client.post("/api/v2/chat/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Hello! I'm doing well, thank you for asking."
        assert data["model"] == "gpt-4o-mini"
        assert data["provider"] == "openai"
        assert "usage" in data
        assert "cost" in data
        assert "response_time" in data
    
    @patch('backend.core.llm_providers.provider_factory.llm_factory')
    def test_chat_completion_batch(self, mock_factory, client):
        """Test batch chat completion endpoint."""
        # Mock the factory response
        mock_factory.chat_with_fallback.return_value = {
            "text": "Batch response",
            "model": "gpt-4o-mini",
            "provider": "openai",
            "usage": {"total_tokens": 15},
            "cost": {"total_cost": 0.01},
            "finish_reason": "stop"
        }
        
        request_data = [
            {
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "gpt-4o-mini"
            },
            {
                "messages": [{"role": "user", "content": "How are you?"}],
                "model": "gpt-4o-mini"
            }
        ]
        
        response = client.post("/api/v2/chat/batch", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "batch_info" in data
        assert len(data["results"]) == 2
    
    @patch('backend.core.llm_providers.provider_factory.llm_factory')
    def test_chat_completion_with_specific_provider(self, mock_factory, client):
        """Test chat completion with specific provider."""
        # Mock the factory response
        mock_factory.get_provider.return_value.chat.return_value = {
            "text": "Mistral response",
            "model": "mistral-small-latest",
            "provider": "mistral",
            "usage": {"total_tokens": 10},
            "cost": {"total_cost": 0.005},
            "finish_reason": "stop"
        }
        
        request_data = {
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "provider": "mistral"
        }
        
        response = client.post("/api/v2/chat/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "mistral"
    
    def test_chat_completion_invalid_request(self, client):
        """Test chat completion with invalid request."""
        request_data = {
            "messages": []  # Empty messages
        }
        
        response = client.post("/api/v2/chat/chat", json=request_data)
        
        assert response.status_code == 400
    
    @patch('backend.core.llm_providers.provider_factory.llm_factory')
    def test_embed_endpoint(self, mock_factory, client):
        """Test embedding endpoint."""
        # Mock the factory response
        mock_factory.embed_with_fallback.return_value = {
            "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "model": "text-embedding-3-small",
            "provider": "openai",
            "usage": {"total_tokens": 20},
            "cost": 0.0004
        }
        
        request_data = {
            "texts": ["Hello world", "Test text"],
            "model": "text-embedding-3-small"
        }
        
        response = client.post("/api/v2/chat/embed", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "embeddings" in data
        assert len(data["embeddings"]) == 2
        assert "cost" in data

class TestOCREndpoints:
    """Test OCR endpoints."""
    
    @patch('backend.core.ocr_providers.ocr_factory.ocr_factory')
    def test_ocr_extract_text(self, mock_factory, client):
        """Test OCR text extraction endpoint."""
        # Mock the factory response
        mock_factory.extract_text_with_fallback.return_value = {
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
        
        # Create a mock file
        files = {"file": ("test.jpg", b"fake_image_data", "image/jpeg")}
        
        response = client.post("/api/v2/ocr/extract", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Sample receipt text extracted from image"
        assert data["confidence"] == 0.95
        assert data["provider"] == "azure_vision"
        assert "cost" in data
    
    def test_ocr_extract_text_no_file(self, client):
        """Test OCR text extraction without file."""
        response = client.post("/api/v2/ocr/extract")
        
        assert response.status_code == 422  # Validation error

class TestVectorStoreEndpoints:
    """Test vector store endpoints."""
    
    @patch('backend.core.vector_stores.pinecone_client.PineconeClient')
    def test_create_index(self, mock_client_class, client):
        """Test vector store index creation."""
        # Mock the client
        mock_client = Mock()
        mock_client.create_index.return_value = True
        mock_client_class.return_value = mock_client
        
        request_data = {
            "provider": "pinecone",
            "index_name": "test-index",
            "dimension": 1536
        }
        
        response = client.post("/api/v2/vector-store/index/create", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["provider"] == "pinecone"
        assert data["index_name"] == "test-index"
    
    @patch('backend.core.vector_stores.pinecone_client.PineconeClient')
    @patch('backend.core.llm_providers.provider_factory.llm_factory')
    def test_upload_documents(self, mock_llm_factory, mock_client_class, client):
        """Test document upload to vector store."""
        # Mock LLM factory for embeddings
        mock_llm_factory.embed_with_fallback.return_value = {
            "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "cost": 0.0004
        }
        
        # Mock vector store client
        mock_client = Mock()
        mock_client.upsert_vectors.return_value = {
            "upserted_count": 2,
            "cost": 0.0002
        }
        mock_client_class.return_value = mock_client
        
        request_data = {
            "documents": [
                {
                    "id": "doc1",
                    "text": "Sample document text",
                    "metadata": {"category": "sample"}
                },
                {
                    "id": "doc2",
                    "text": "Another document",
                    "metadata": {"category": "sample"}
                }
            ],
            "index_name": "test-index",
            "provider": "pinecone"
        }
        
        response = client.post("/api/v2/vector-store/documents/upload", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["documents_uploaded"] == 2
        assert "embedding_cost" in data
        assert "vector_store_cost" in data
        assert "total_cost" in data
    
    @patch('backend.core.vector_stores.pinecone_client.PineconeClient')
    @patch('backend.core.llm_providers.provider_factory.llm_factory')
    def test_search_documents(self, mock_llm_factory, mock_client_class, client):
        """Test document search in vector store."""
        # Mock LLM factory for query embedding
        mock_llm_factory.embed_with_fallback.return_value = {
            "embeddings": [[0.1, 0.2, 0.3]],
            "cost": 0.0002
        }
        
        # Mock vector store client
        mock_client = Mock()
        mock_client.query_vectors.return_value = {
            "matches": [
                {
                    "id": "doc1",
                    "score": 0.95,
                    "metadata": {"text": "Sample document text"}
                }
            ],
            "cost": 0.0001
        }
        mock_client_class.return_value = mock_client
        
        request_data = {
            "query": "sample document",
            "index_name": "test-index",
            "top_k": 5
        }
        
        response = client.post("/api/v2/vector-store/search", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "sample document"
        assert len(data["results"]) == 1
        assert data["results"][0]["id"] == "doc1"
        assert "embedding_cost" in data
        assert "search_cost" in data
        assert "total_cost" in data
    
    @patch('backend.core.vector_stores.pinecone_client.PineconeClient')
    def test_list_indexes(self, mock_client_class, client):
        """Test listing vector store indexes."""
        # Mock the client
        mock_client = Mock()
        mock_client.list_indexes.return_value = ["index1", "index2"]
        mock_client_class.return_value = mock_client
        
        response = client.get("/api/v2/vector-store/indexes/pinecone")
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "pinecone"
        assert "index1" in data["indexes"]
        assert "index2" in data["indexes"]
    
    @patch('backend.core.vector_stores.pinecone_client.PineconeClient')
    def test_describe_index(self, mock_client_class, client):
        """Test describing vector store index."""
        # Mock the client
        mock_client = Mock()
        mock_client.describe_index.return_value = {
            "name": "test-index",
            "dimension": 1536,
            "index_size": 1000,
            "provider": "pinecone"
        }
        mock_client_class.return_value = mock_client
        
        response = client.get("/api/v2/vector-store/index/pinecone/test-index")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test-index"
        assert data["dimension"] == 1536
        assert data["provider"] == "pinecone"

class TestSetupEndpoints:
    """Test setup and configuration endpoints."""
    
    def test_setup_providers(self, client):
        """Test provider setup endpoint."""
        response = client.post("/api/v1/setup")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
        assert "llm_providers" in data
        assert "ocr_providers" in data
    
    def test_get_cost_info(self, client):
        """Test cost information endpoint."""
        response = client.get("/api/v1/costs")
        
        assert response.status_code == 200
        data = response.json()
        assert "llm_providers" in data
        assert "ocr_providers" in data
        assert "vector_stores" in data

class TestErrorHandling:
    """Test error handling in API endpoints."""
    
    def test_invalid_endpoint(self, client):
        """Test invalid endpoint handling."""
        response = client.get("/invalid/endpoint")
        
        assert response.status_code == 404
    
    @patch('backend.core.llm_providers.provider_factory.llm_factory')
    def test_chat_completion_provider_error(self, mock_factory, client):
        """Test chat completion with provider error."""
        # Mock factory to raise exception
        mock_factory.chat_with_fallback.side_effect = Exception("Provider error")
        
        request_data = {
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = client.post("/api/v2/chat/chat", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
    
    def test_rate_limiting(self, client):
        """Test rate limiting."""
        # Make multiple requests to trigger rate limiting
        for _ in range(15):  # Exceed the rate limit
            response = client.get("/")
        
        # The last request should be rate limited
        assert response.status_code == 429 