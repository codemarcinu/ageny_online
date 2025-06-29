from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import time
import json

from ....config import get_settings, get_provider_config
from ....core.vector_stores.pinecone_client import PineconeClient
from ....core.vector_stores.weaviate_client import WeaviateClient
from ....core.llm_providers.provider_factory import llm_factory

logger = logging.getLogger(__name__)

router = APIRouter()

settings = get_settings()

class VectorStoreConfig(BaseModel):
    """Vector store configuration model."""
    provider: str = Field(..., description="Vector store provider (pinecone, weaviate)")
    index_name: str = Field(..., description="Index/collection name")
    dimension: int = Field(1536, description="Vector dimension")

class Document(BaseModel):
    """Document model for vector storage."""
    id: str = Field(..., description="Document ID")
    text: str = Field(..., description="Document text")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Document metadata")

class SearchRequest(BaseModel):
    """Vector search request model."""
    query: str = Field(..., description="Search query")
    index_name: str = Field(..., description="Index/collection name")
    provider: Optional[str] = Field(None, description="Specific provider to use")
    top_k: int = Field(10, description="Number of results to return")
    filter: Optional[Dict[str, Any]] = Field(None, description="Metadata filter")

class SearchResult(BaseModel):
    """Vector search result model."""
    id: str
    score: float
    text: str
    metadata: Dict[str, Any]

class UploadDocumentsRequest(BaseModel):
    """Upload documents request model."""
    documents: List[Document] = Field(..., description="List of documents to upload")
    index_name: str = Field(..., description="Index/collection name")
    provider: str = Field("pinecone", description="Vector store provider")

# Initialize vector store clients
vector_stores = {}

def get_pinecone_client():
    """Get or create Pinecone client."""
    if "pinecone" not in vector_stores:
        config = get_provider_config("pinecone")
        if config.get("api_key"):
            vector_stores["pinecone"] = PineconeClient(
                api_key=config["api_key"],
                environment=config.get("environment", "gcp-starter")
            )
    return vector_stores.get("pinecone")

def get_weaviate_client():
    """Get or create Weaviate client."""
    if "weaviate" not in vector_stores:
        config = get_provider_config("weaviate")
        if config.get("url"):
            vector_stores["weaviate"] = WeaviateClient(
                url=config["url"],
                api_key=config.get("api_key"),
                username=config.get("username"),
                password=config.get("password")
            )
    return vector_stores.get("weaviate")

@router.post("/index/create")
async def create_index(config: VectorStoreConfig):
    """
    Create a new vector store index.
    """
    try:
        if config.provider == "pinecone":
            client = get_pinecone_client()
            if not client:
                raise HTTPException(status_code=400, detail="Pinecone not configured")
            
            success = await client.create_index(
                index_name=config.index_name,
                dimension=config.dimension
            )
            
        elif config.provider == "weaviate":
            client = get_weaviate_client()
            if not client:
                raise HTTPException(status_code=400, detail="Weaviate not configured")
            
            success = await client.create_collection(
                collection_name=config.index_name
            )
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {config.provider}")
        
        return {
            "success": success,
            "provider": config.provider,
            "index_name": config.index_name
        }
        
    except Exception as e:
        logger.error(f"Failed to create index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create index: {str(e)}")

@router.delete("/index/{provider}/{index_name}")
async def delete_index(provider: str, index_name: str):
    """
    Delete a vector store index.
    """
    try:
        if provider == "pinecone":
            client = get_pinecone_client()
            if not client:
                raise HTTPException(status_code=400, detail="Pinecone not configured")
            
            success = await client.delete_index(index_name)
            
        elif provider == "weaviate":
            client = get_weaviate_client()
            if not client:
                raise HTTPException(status_code=400, detail="Weaviate not configured")
            
            success = await client.delete_collection(index_name)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        return {
            "success": success,
            "provider": provider,
            "index_name": index_name
        }
        
    except Exception as e:
        logger.error(f"Failed to delete index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete index: {str(e)}")

@router.post("/documents/upload")
async def upload_documents(request: UploadDocumentsRequest):
    """
    Upload documents to vector store with automatic embedding generation.
    """
    try:
        if not request.documents:
            raise HTTPException(status_code=400, detail="At least one document is required")
        
        # Generate embeddings for documents
        texts = [doc.text for doc in request.documents]
        embedding_result = await llm_factory.embed_with_fallback(texts=texts)
        embeddings = embedding_result["embeddings"]
        
        # Prepare vectors for upload
        vectors = []
        for i, doc in enumerate(request.documents):
            vector_data = {
                "id": doc.id,
                "values": embeddings[i],
                "metadata": {
                    "text": doc.text,
                    **doc.metadata
                }
            }
            vectors.append(vector_data)
        
        # Upload to vector store
        if request.provider == "pinecone":
            client = get_pinecone_client()
            if not client:
                raise HTTPException(status_code=400, detail="Pinecone not configured")
            
            result = await client.upsert_vectors(
                index_name=request.index_name,
                vectors=vectors
            )
            
        elif request.provider == "weaviate":
            client = get_weaviate_client()
            if not client:
                raise HTTPException(status_code=400, detail="Weaviate not configured")
            
            # Convert to Weaviate format
            objects = []
            for doc in request.documents:
                obj = {
                    "id": doc.id,
                    "text": doc.text,
                    **doc.metadata
                }
                objects.append(obj)
            
            result = await client.insert_objects(
                collection_name=request.index_name,
                objects=objects
            )
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")
        
        return {
            "success": True,
            "provider": request.provider,
            "index_name": request.index_name,
            "documents_uploaded": len(request.documents),
            "embedding_cost": embedding_result.get("cost", 0),
            "vector_store_cost": result.get("cost", 0),
            "total_cost": embedding_result.get("cost", 0) + result.get("cost", 0)
        }
        
    except Exception as e:
        logger.error(f"Failed to upload documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload documents: {str(e)}")

@router.post("/search")
async def search_documents(request: SearchRequest):
    """
    Search documents in vector store.
    """
    try:
        # Generate embedding for query
        embedding_result = await llm_factory.embed_with_fallback([request.query])
        query_embedding = embedding_result["embeddings"][0]
        
        # Determine provider to use
        provider = request.provider or "pinecone"
        
        if provider == "pinecone":
            client = get_pinecone_client()
            if not client:
                raise HTTPException(status_code=400, detail="Pinecone not configured")
            
            result = await client.query_vectors(
                index_name=request.index_name,
                vector=query_embedding,
                top_k=request.top_k,
                filter=request.filter
            )
            
            # Convert to standard format
            matches = []
            for match in result["matches"]:
                matches.append(SearchResult(
                    id=match.id,
                    score=match.score,
                    text=match.metadata.get("text", ""),
                    metadata=match.metadata
                ))
            
        elif provider == "weaviate":
            client = get_weaviate_client()
            if not client:
                raise HTTPException(status_code=400, detail="Weaviate not configured")
            
            result = await client.query_objects(
                collection_name=request.index_name,
                query_text=request.query,
                limit=request.top_k
            )
            
            # Convert to standard format
            matches = []
            for match in result["matches"]:
                matches.append(SearchResult(
                    id=match.id,
                    score=match.score,
                    text=match.metadata.get("text", ""),
                    metadata=match.metadata
                ))
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        return {
            "query": request.query,
            "provider": provider,
            "index_name": request.index_name,
            "results": matches,
            "embedding_cost": embedding_result.get("cost", 0),
            "search_cost": result.get("cost", 0),
            "total_cost": embedding_result.get("cost", 0) + result.get("cost", 0)
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/indexes/{provider}")
async def list_indexes(provider: str):
    """
    List all indexes for a specific provider.
    """
    try:
        if provider == "pinecone":
            client = get_pinecone_client()
            if not client:
                raise HTTPException(status_code=400, detail="Pinecone not configured")
            
            indexes = client.list_indexes()
            
        elif provider == "weaviate":
            client = get_weaviate_client()
            if not client:
                raise HTTPException(status_code=400, detail="Weaviate not configured")
            
            indexes = client.list_collections()
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        return {
            "provider": provider,
            "indexes": indexes
        }
        
    except Exception as e:
        logger.error(f"Failed to list indexes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list indexes: {str(e)}")

@router.get("/index/{provider}/{index_name}")
async def describe_index(provider: str, index_name: str):
    """
    Get information about a specific index.
    """
    try:
        if provider == "pinecone":
            client = get_pinecone_client()
            if not client:
                raise HTTPException(status_code=400, detail="Pinecone not configured")
            
            info = await client.describe_index(index_name)
            
        elif provider == "weaviate":
            client = get_weaviate_client()
            if not client:
                raise HTTPException(status_code=400, detail="Weaviate not configured")
            
            info = await client.describe_collection(index_name)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        return info
        
    except Exception as e:
        logger.error(f"Failed to describe index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to describe index: {str(e)}")

@router.get("/providers/status")
async def get_vector_store_status():
    """Get status of all vector store providers."""
    try:
        status = {}
        
        # Check Pinecone
        pinecone_client = get_pinecone_client()
        status["pinecone"] = {
            "configured": pinecone_client is not None,
            "available": pinecone_client is not None
        }
        
        # Check Weaviate
        weaviate_client = get_weaviate_client()
        status["weaviate"] = {
            "configured": weaviate_client is not None,
            "available": weaviate_client is not None
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get vector store status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get vector store status") 