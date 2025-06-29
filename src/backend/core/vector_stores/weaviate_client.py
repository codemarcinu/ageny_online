import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import weaviate
from weaviate import Client

logger = logging.getLogger(__name__)

@dataclass
class VectorSearchResult:
    """Result of vector search."""
    id: str
    score: float
    metadata: Dict[str, Any]
    vector: Optional[List[float]] = None

class WeaviateClient:
    """Weaviate vector database client."""
    
    def __init__(self, url: str, api_key: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Weaviate client.
        
        Args:
            url: Weaviate server URL
            api_key: API key for authentication (optional)
            username: Username for authentication (optional)
            password: Password for authentication (optional)
        """
        if not url:
            raise ValueError("Weaviate URL is required")
        
        # Setup authentication
        auth = None
        if api_key:
            auth = weaviate.auth.AuthApiKey(api_key)
        elif username and password:
            auth = weaviate.auth.AuthClientPassword(username, password)
        
        # Initialize client
        self.client = weaviate.Client(
            url=url,
            auth_client_secret=auth
        )
        
        # Cost per 1000 operations (estimated for self-hosted)
        self.cost_per_1k_operations = 0.05  # USD (self-hosted cost)
        
        logger.info(f"Weaviate client initialized with URL: {url}")
    
    async def create_collection(
        self, 
        collection_name: str, 
        vectorizer: str = "text2vec-openai",
        **kwargs
    ) -> bool:
        """
        Create a new Weaviate collection.
        
        Args:
            collection_name: Name of the collection
            vectorizer: Vectorizer to use
            **kwargs: Additional parameters
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Creating Weaviate collection: {collection_name}")
            
            # Check if collection already exists
            if self.client.schema.exists(collection_name):
                logger.warning(f"Collection {collection_name} already exists")
                return True
            
            # Create collection schema
            class_obj = {
                "class": collection_name,
                "vectorizer": vectorizer,
                **kwargs
            }
            
            # Create collection
            await asyncio.to_thread(
                self.client.schema.create_class,
                class_obj
            )
            
            logger.info(f"Successfully created collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            raise
    
    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a Weaviate collection.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Deleting Weaviate collection: {collection_name}")
            
            await asyncio.to_thread(
                self.client.schema.delete_class,
                collection_name
            )
            
            logger.info(f"Successfully deleted collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            raise
    
    def get_collection(self, collection_name: str):
        """
        Get a Weaviate collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Weaviate collection object
        """
        try:
            return self.client.collections.get(collection_name)
        except Exception as e:
            logger.error(f"Error getting collection {collection_name}: {e}")
            raise
    
    async def insert_objects(
        self,
        collection_name: str,
        objects: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Insert objects into Weaviate collection.
        
        Args:
            collection_name: Name of the collection
            objects: List of objects to insert
            **kwargs: Additional parameters
            
        Returns:
            Insert result with cost info
        """
        try:
            logger.debug(f"Inserting {len(objects)} objects to collection: {collection_name}")
            
            collection = self.get_collection(collection_name)
            
            result = await asyncio.to_thread(
                collection.data.insert_many,
                objects,
                **kwargs
            )
            
            # Calculate cost (1 operation per object)
            cost = (len(objects) / 1000) * self.cost_per_1k_operations
            
            response = {
                "inserted_count": len(result),
                "provider": "weaviate",
                "cost": cost,
                "raw_result": result
            }
            
            logger.info(f"Inserted {len(result)} objects. Cost: ${cost:.4f}")
            return response
            
        except Exception as e:
            logger.error(f"Error inserting objects: {e}")
            raise
    
    async def query_objects(
        self,
        collection_name: str,
        query_text: str,
        limit: int = 10,
        additional_properties: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Query objects from Weaviate collection.
        
        Args:
            collection_name: Name of the collection
            query_text: Text to search for
            limit: Number of results to return
            additional_properties: Additional properties to include
            **kwargs: Additional parameters
            
        Returns:
            Query result with cost info
        """
        try:
            logger.debug(f"Querying objects from collection: {collection_name}")
            
            collection = self.get_collection(collection_name)
            
            # Build query
            query = collection.query.near_text(
                query=query_text,
                limit=limit,
                additional_properties=additional_properties or [],
                **kwargs
            )
            
            result = await asyncio.to_thread(query.do)
            
            # Calculate cost (1 operation per query)
            cost = self.cost_per_1k_operations / 1000
            
            # Process results
            matches = []
            for obj in result.objects:
                matches.append(VectorSearchResult(
                    id=obj.uuid,
                    score=obj.metadata.score if hasattr(obj.metadata, 'score') else 0.0,
                    metadata=obj.properties,
                    vector=obj.vector if hasattr(obj, 'vector') else None
                ))
            
            response = {
                "matches": matches,
                "provider": "weaviate",
                "cost": cost,
                "raw_result": result
            }
            
            logger.info(f"Query returned {len(matches)} results. Cost: ${cost:.4f}")
            return response
            
        except Exception as e:
            logger.error(f"Error querying objects: {e}")
            raise
    
    async def delete_objects(
        self,
        collection_name: str,
        where_filter: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Delete objects from Weaviate collection.
        
        Args:
            collection_name: Name of the collection
            where_filter: Filter to select objects to delete
            **kwargs: Additional parameters
            
        Returns:
            Delete result with cost info
        """
        try:
            logger.debug(f"Deleting objects from collection: {collection_name}")
            
            collection = self.get_collection(collection_name)
            
            result = await asyncio.to_thread(
                collection.data.delete_many,
                where=where_filter,
                **kwargs
            )
            
            # Calculate cost (1 operation per deletion)
            cost = self.cost_per_1k_operations / 1000
            
            response = {
                "deleted_count": result,
                "provider": "weaviate",
                "cost": cost,
                "raw_result": result
            }
            
            logger.info(f"Deleted {result} objects. Cost: ${cost:.4f}")
            return response
            
        except Exception as e:
            logger.error(f"Error deleting objects: {e}")
            raise
    
    async def describe_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Get collection description.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection description
        """
        try:
            collection = self.get_collection(collection_name)
            config = collection.config.get()
            
            return {
                "name": collection_name,
                "vectorizer": config.vectorizer,
                "properties": [prop.name for prop in config.properties],
                "provider": "weaviate"
            }
            
        except Exception as e:
            logger.error(f"Error describing collection: {e}")
            raise
    
    def list_collections(self) -> List[str]:
        """Get list of all collections."""
        try:
            return [col.name for col in self.client.collections.list_all()]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            raise
    
    def get_cost_info(self) -> Dict[str, Any]:
        """Get cost information."""
        return {
            "cost_per_1k_operations": self.cost_per_1k_operations,
            "currency": "USD",
            "provider": "weaviate",
            "note": "Self-hosted cost estimate"
        } 