import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import pinecone

logger = logging.getLogger(__name__)

@dataclass
class VectorSearchResult:
    """Result of vector search."""
    id: str
    score: float
    metadata: Dict[str, Any]
    vector: Optional[List[float]] = None

class PineconeClient:
    """Pinecone vector database client."""
    
    def __init__(self, api_key: str, environment: str = "gcp-starter"):
        """
        Initialize Pinecone client.
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
        """
        if not api_key:
            raise ValueError("Pinecone API key is required")
        
        # Initialize Pinecone with the old API
        pinecone.init(api_key=api_key, environment=environment)
        self.environment = environment
        
        # Cost per 1000 operations (as of 2024)
        self.cost_per_1k_operations = 0.10  # USD
        
        logger.info(f"Pinecone client initialized with environment: {environment}")
    
    async def create_index(
        self, 
        index_name: str, 
        dimension: int = 1536,
        metric: str = "cosine",
        **kwargs
    ) -> bool:
        """
        Create a new Pinecone index.
        
        Args:
            index_name: Name of the index
            dimension: Vector dimension
            metric: Distance metric (cosine, euclidean, dotproduct)
            **kwargs: Additional parameters
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Creating Pinecone index: {index_name}")
            
            # Check if index already exists
            if index_name in pinecone.list_indexes():
                logger.warning(f"Index {index_name} already exists")
                return True
            
            # Create index
            await asyncio.to_thread(
                pinecone.create_index,
                name=index_name,
                dimension=dimension,
                metric=metric,
                **kwargs
            )
            
            logger.info(f"Successfully created index: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
            raise
    
    async def delete_index(self, index_name: str) -> bool:
        """
        Delete a Pinecone index.
        
        Args:
            index_name: Name of the index to delete
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Deleting Pinecone index: {index_name}")
            
            await asyncio.to_thread(
                pinecone.delete_index,
                index_name
            )
            
            logger.info(f"Successfully deleted index: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting index {index_name}: {e}")
            raise
    
    def get_index(self, index_name: str):
        """
        Get a Pinecone index.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Pinecone index object
        """
        try:
            return pinecone.Index(index_name)
        except Exception as e:
            logger.error(f"Error getting index {index_name}: {e}")
            raise
    
    async def upsert_vectors(
        self,
        index_name: str,
        vectors: List[Dict[str, Any]],
        namespace: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upsert vectors to Pinecone index.
        
        Args:
            index_name: Name of the index
            vectors: List of vector dictionaries with 'id', 'values', and 'metadata'
            namespace: Namespace for the vectors
            **kwargs: Additional parameters
            
        Returns:
            Upsert result with cost info
        """
        try:
            logger.debug(f"Upserting {len(vectors)} vectors to index: {index_name}")
            
            index = self.get_index(index_name)
            
            result = await asyncio.to_thread(
                index.upsert,
                vectors=vectors,
                namespace=namespace,
                **kwargs
            )
            
            # Calculate cost (1 operation per vector)
            cost = (len(vectors) / 1000) * self.cost_per_1k_operations
            
            response = {
                "upserted_count": result.upserted_count,
                "provider": "pinecone",
                "cost": cost,
                "raw_result": result
            }
            
            logger.info(f"Upserted {result.upserted_count} vectors. Cost: ${cost:.4f}")
            return response
            
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            raise
    
    async def query_vectors(
        self,
        index_name: str,
        vector: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_values: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Query vectors from Pinecone index.
        
        Args:
            index_name: Name of the index
            vector: Query vector
            top_k: Number of results to return
            namespace: Namespace to query
            filter: Metadata filter
            include_metadata: Include metadata in results
            include_values: Include vector values in results
            **kwargs: Additional parameters
            
        Returns:
            Query result with cost info
        """
        try:
            logger.debug(f"Querying vectors from index: {index_name}")
            
            index = self.get_index(index_name)
            
            result = await asyncio.to_thread(
                index.query,
                vector=vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=include_metadata,
                include_values=include_values,
                **kwargs
            )
            
            # Calculate cost (1 operation per query)
            cost = self.cost_per_1k_operations / 1000
            
            # Process results
            matches = []
            for match in result.matches:
                matches.append(VectorSearchResult(
                    id=match.id,
                    score=match.score,
                    metadata=match.metadata if match.metadata else {},
                    vector=match.values if include_values else None
                ))
            
            response = {
                "matches": matches,
                "namespace": result.namespace,
                "provider": "pinecone",
                "cost": cost,
                "raw_result": result
            }
            
            logger.info(f"Query returned {len(matches)} results. Cost: ${cost:.4f}")
            return response
            
        except Exception as e:
            logger.error(f"Error querying vectors: {e}")
            raise
    
    async def delete_vectors(
        self,
        index_name: str,
        ids: List[str],
        namespace: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Delete vectors from Pinecone index.
        
        Args:
            index_name: Name of the index
            ids: List of vector IDs to delete
            namespace: Namespace for the vectors
            **kwargs: Additional parameters
            
        Returns:
            Delete result with cost info
        """
        try:
            logger.debug(f"Deleting {len(ids)} vectors from index: {index_name}")
            
            index = self.get_index(index_name)
            
            result = await asyncio.to_thread(
                index.delete,
                ids=ids,
                namespace=namespace,
                **kwargs
            )
            
            # Calculate cost (1 operation per vector)
            cost = (len(ids) / 1000) * self.cost_per_1k_operations
            
            response = {
                "deleted_count": len(ids),
                "provider": "pinecone",
                "cost": cost,
                "raw_result": result
            }
            
            logger.info(f"Deleted {len(ids)} vectors. Cost: ${cost:.4f}")
            return response
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            raise
    
    async def describe_index(self, index_name: str) -> Dict[str, Any]:
        """
        Get index description.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Index description
        """
        try:
            index = self.get_index(index_name)
            stats = await asyncio.to_thread(index.describe_index_stats)
            
            return {
                "name": index_name,
                "dimension": stats.dimension,
                "index_size": stats.index_size,
                "namespaces": stats.namespaces,
                "provider": "pinecone"
            }
            
        except Exception as e:
            logger.error(f"Error describing index: {e}")
            raise
    
    def list_indexes(self) -> List[str]:
        """Get list of all indexes."""
        try:
            return pinecone.list_indexes()
        except Exception as e:
            logger.error(f"Error listing indexes: {e}")
            raise
    
    def get_cost_info(self) -> Dict[str, Any]:
        """Get cost information."""
        return {
            "cost_per_1k_operations": self.cost_per_1k_operations,
            "currency": "USD",
            "provider": "pinecone"
        } 