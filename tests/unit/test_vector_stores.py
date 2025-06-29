import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from backend.core.vector_stores.pinecone_client import PineconeClient, VectorSearchResult
from backend.core.vector_stores.weaviate_client import WeaviateClient

class TestPineconeClient:
    """Test cases for Pinecone client."""
    
    def test_pinecone_client_initialization(self):
        """Test Pinecone client initialization."""
        client = PineconeClient("test-api-key", "test-environment")
        
        assert client.cost_per_1k_operations == 0.10
        assert client.environment == "test-environment"
    
    def test_pinecone_client_initialization_without_key(self):
        """Test Pinecone client initialization without API key."""
        with pytest.raises(ValueError, match="Pinecone API key is required"):
            PineconeClient("", "test-environment")
    
    @pytest.mark.asyncio
    async def test_pinecone_create_index(self):
        """Test Pinecone index creation."""
        with patch('backend.core.vector_stores.pinecone_client.pinecone') as mock_pinecone:
            # Mock the old API
            mock_pinecone.list_indexes.return_value = []
            mock_pinecone.create_index.return_value = None
            
            client = PineconeClient("test-api-key", "test-environment")
            
            result = await client.create_index("test-index", 1536)
            
            assert result == True
    
    @pytest.mark.asyncio
    async def test_pinecone_create_index_already_exists(self):
        """Test Pinecone index creation when index already exists."""
        with patch('backend.core.vector_stores.pinecone_client.pinecone') as mock_pinecone:
            # Mock the old API
            mock_pinecone.list_indexes.return_value = ["test-index"]
            
            client = PineconeClient("test-api-key", "test-environment")
            
            result = await client.create_index("test-index", 1536)
            
            assert result == True
    
    @pytest.mark.asyncio
    async def test_pinecone_upsert_vectors(self):
        """Test Pinecone vector upserting."""
        with patch('backend.core.vector_stores.pinecone_client.pinecone') as mock_pinecone:
            # Setup mock index
            mock_index = Mock()
            mock_result = Mock()
            mock_result.upserted_count = 2
            mock_index.upsert.return_value = mock_result
            
            mock_pinecone.Index.return_value = mock_index
            
            client = PineconeClient("test-api-key", "test-environment")
            
            vectors = [
                {
                    "id": "vec1",
                    "values": [0.1, 0.2, 0.3],
                    "metadata": {"text": "sample"}
                },
                {
                    "id": "vec2",
                    "values": [0.4, 0.5, 0.6],
                    "metadata": {"text": "sample2"}
                }
            ]
            
            result = await client.upsert_vectors("test-index", vectors)
            
            assert result["upserted_count"] == 2
            assert result["provider"] == "pinecone"
            assert "cost" in result
    
    @pytest.mark.asyncio
    async def test_pinecone_query_vectors(self):
        """Test Pinecone vector querying."""
        with patch('backend.core.vector_stores.pinecone_client.pinecone') as mock_pinecone:
            # Setup mock index
            mock_index = Mock()
            mock_match = Mock()
            mock_match.id = "vec1"
            mock_match.score = 0.95
            mock_match.metadata = {"text": "sample"}
            
            mock_result = Mock()
            mock_result.matches = [mock_match]
            mock_result.namespace = "test-namespace"
            
            mock_index.query.return_value = mock_result
            
            mock_pinecone.Index.return_value = mock_index
            
            client = PineconeClient("test-api-key", "test-environment")
            
            query_vector = [0.1, 0.2, 0.3]
            result = await client.query_vectors("test-index", query_vector, top_k=5)
            
            assert len(result["matches"]) == 1
            assert result["matches"][0].id == "vec1"
            assert result["matches"][0].score == 0.95
            assert result["provider"] == "pinecone"
            assert "cost" in result
    
    @pytest.mark.asyncio
    async def test_pinecone_delete_vectors(self):
        """Test Pinecone vector deletion."""
        with patch('backend.core.vector_stores.pinecone_client.pinecone') as mock_pinecone:
            # Setup mock index
            mock_index = Mock()
            mock_index.delete.return_value = None
            
            mock_pinecone.Index.return_value = mock_index
            
            client = PineconeClient("test-api-key", "test-environment")
            
            ids = ["vec1", "vec2"]
            result = await client.delete_vectors("test-index", ids)
            
            assert result["deleted_count"] == 2
            assert result["provider"] == "pinecone"
            assert "cost" in result
    
    def test_pinecone_list_indexes(self):
        """Test listing Pinecone indexes."""
        with patch('backend.core.vector_stores.pinecone_client.pinecone') as mock_pinecone:
            mock_pinecone.list_indexes.return_value = ["index1", "index2"]
            
            client = PineconeClient("test-api-key", "test-environment")
            
            indexes = client.list_indexes()
            
            assert "index1" in indexes
            assert "index2" in indexes
    
    def test_pinecone_get_cost_info(self):
        """Test getting Pinecone cost information."""
        client = PineconeClient("test-api-key", "test-environment")
        cost_info = client.get_cost_info()
        
        assert cost_info["cost_per_1k_operations"] == 0.10
        assert cost_info["currency"] == "USD"
        assert cost_info["provider"] == "pinecone"

class TestWeaviateClient:
    """Test cases for Weaviate client."""
    
    def test_weaviate_client_initialization(self):
        """Test Weaviate client initialization."""
        with patch('backend.core.vector_stores.weaviate_client.weaviate') as mock_weaviate:
            # Mock the client to avoid real network connections
            mock_client = Mock()
            mock_weaviate.Client.return_value = mock_client
            
            client = WeaviateClient("https://test.weaviate.network")
            
            assert client.cost_per_1k_operations == 0.05
    
    def test_weaviate_client_initialization_without_url(self):
        """Test Weaviate client initialization without URL."""
        with pytest.raises(ValueError, match="Weaviate URL is required"):
            WeaviateClient("")
    
    @pytest.mark.asyncio
    async def test_weaviate_create_collection(self):
        """Test Weaviate collection creation."""
        with patch('backend.core.vector_stores.weaviate_client.weaviate') as mock_weaviate:
            # Setup mock client
            mock_client = Mock()
            mock_client.schema.exists.return_value = False
            mock_client.schema.create_class.return_value = None
            mock_weaviate.Client.return_value = mock_client
            
            client = WeaviateClient("https://test.weaviate.network")
            
            result = await client.create_collection("test-collection")
            
            assert result == True
    
    @pytest.mark.asyncio
    async def test_weaviate_create_collection_already_exists(self):
        """Test Weaviate collection creation when collection already exists."""
        with patch('backend.core.vector_stores.weaviate_client.weaviate') as mock_weaviate:
            # Setup mock client
            mock_client = Mock()
            mock_client.schema.exists.return_value = True
            mock_weaviate.Client.return_value = mock_client
            
            client = WeaviateClient("https://test.weaviate.network")
            
            result = await client.create_collection("test-collection")
            
            assert result == True
    
    @pytest.mark.asyncio
    async def test_weaviate_insert_objects(self):
        """Test Weaviate object insertion."""
        with patch('backend.core.vector_stores.weaviate_client.weaviate') as mock_weaviate:
            # Setup mock client and collection
            mock_collection = Mock()
            mock_collection.data.insert_many.return_value = [1, 2]  # Return inserted IDs
            
            mock_client = Mock()
            mock_client.collections.get.return_value = mock_collection
            mock_weaviate.Client.return_value = mock_client
            
            client = WeaviateClient("https://test.weaviate.network")
            
            objects = [
                {
                    "id": "obj1",
                    "text": "sample text",
                    "category": "test"
                },
                {
                    "id": "obj2",
                    "text": "sample text 2",
                    "category": "test"
                }
            ]
            
            result = await client.insert_objects("test-collection", objects)
            
            assert result["inserted_count"] == 2
            assert result["provider"] == "weaviate"
            assert "cost" in result
    
    @pytest.mark.asyncio
    async def test_weaviate_query_objects(self):
        """Test Weaviate object querying."""
        with patch('backend.core.vector_stores.weaviate_client.weaviate') as mock_weaviate:
            # Setup mock client and collection
            mock_collection = Mock()
            mock_query = Mock()
            mock_query.do.return_value = Mock()
            mock_query.do.return_value.objects = [Mock(), Mock()]
            
            # Setup mock objects
            for i, obj in enumerate(mock_query.do.return_value.objects):
                obj.uuid = f"obj{i+1}"
                obj.properties = {"text": f"sample text {i+1}"}
                obj.metadata = Mock()
                obj.metadata.score = 0.9 - (i * 0.1)
            
            mock_collection.query.near_text.return_value = mock_query
            
            mock_client = Mock()
            mock_client.collections.get.return_value = mock_collection
            mock_weaviate.Client.return_value = mock_client
            
            client = WeaviateClient("https://test.weaviate.network")
            
            result = await client.query_objects("test-collection", "sample query", limit=5)
            
            assert len(result["matches"]) == 2
            assert result["provider"] == "weaviate"
            assert "cost" in result
    
    @pytest.mark.asyncio
    async def test_weaviate_delete_objects(self):
        """Test Weaviate object deletion."""
        with patch('backend.core.vector_stores.weaviate_client.weaviate') as mock_weaviate:
            # Setup mock client and collection
            mock_collection = Mock()
            mock_collection.data.delete_many.return_value = 2  # Return deleted count
            
            mock_client = Mock()
            mock_client.collections.get.return_value = mock_collection
            mock_weaviate.Client.return_value = mock_client
            
            client = WeaviateClient("https://test.weaviate.network")
            
            where_filter = {"category": "test"}
            result = await client.delete_objects("test-collection", where_filter)
            
            assert result["deleted_count"] == 2
            assert result["provider"] == "weaviate"
            assert "cost" in result
    
    def test_weaviate_list_collections(self):
        """Test listing Weaviate collections."""
        with patch('backend.core.vector_stores.weaviate_client.weaviate') as mock_weaviate:
            # Setup mock client with proper collection objects
            mock_collection1 = Mock()
            mock_collection1.name = "collection1"
            mock_collection2 = Mock()
            mock_collection2.name = "collection2"
            
            mock_client = Mock()
            mock_client.collections.list_all.return_value = [mock_collection1, mock_collection2]
            mock_weaviate.Client.return_value = mock_client
            
            client = WeaviateClient("https://test.weaviate.network")
            
            collections = client.list_collections()
            
            assert "collection1" in collections
            assert "collection2" in collections
    
    def test_weaviate_get_cost_info(self):
        """Test getting Weaviate cost information."""
        with patch('backend.core.vector_stores.weaviate_client.weaviate') as mock_weaviate:
            # Mock the client to avoid real network connections
            mock_client = Mock()
            mock_weaviate.Client.return_value = mock_client
            
            client = WeaviateClient("https://test.weaviate.network")
            cost_info = client.get_cost_info()
            
            assert cost_info["cost_per_1k_operations"] == 0.05
            assert cost_info["currency"] == "USD"
            assert cost_info["provider"] == "weaviate"

class TestVectorSearchResult:
    """Test cases for VectorSearchResult dataclass."""
    
    def test_vector_search_result_creation(self):
        """Test VectorSearchResult creation."""
        result = VectorSearchResult(
            id="test-id",
            score=0.95,
            metadata={"text": "sample"},
            vector=[0.1, 0.2, 0.3]
        )
        
        assert result.id == "test-id"
        assert result.score == 0.95
        assert result.metadata["text"] == "sample"
        assert result.vector == [0.1, 0.2, 0.3]
    
    def test_vector_search_result_without_vector(self):
        """Test VectorSearchResult creation without vector."""
        result = VectorSearchResult(
            id="test-id",
            score=0.95,
            metadata={"text": "sample"}
        )
        
        assert result.id == "test-id"
        assert result.score == 0.95
        assert result.vector is None 