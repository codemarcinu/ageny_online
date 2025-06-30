from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import aiohttp
import asyncio
from datetime import datetime
import json

from backend.core.llm_providers.provider_factory import LLMProviderFactory, ProviderType

logger = logging.getLogger(__name__)

router = APIRouter()

class WebSearchRequest(BaseModel):
    """Web search request model."""
    query: str = Field(..., description="Search query")
    max_results: int = Field(5, description="Maximum number of results to return", ge=1, le=10)
    search_engine: str = Field("duckduckgo", description="Search engine to use")

class WebSearchResult(BaseModel):
    """Web search result model."""
    title: str
    url: str
    snippet: str
    source: str
    timestamp: str

class WebSearchResponse(BaseModel):
    """Web search response model."""
    query: str
    results: List[WebSearchResult]
    total_results: int
    search_engine: str
    search_time: float

class WebSearchProvider:
    """Base class for web search providers."""
    
    async def search(self, query: str, max_results: int) -> List[WebSearchResult]:
        """Perform web search and return results."""
        raise NotImplementedError

class DuckDuckGoProvider(WebSearchProvider):
    """DuckDuckGo search provider using their Instant Answer API."""
    
    async def search(self, query: str, max_results: int) -> List[WebSearchResult]:
        """Search using DuckDuckGo Instant Answer API."""
        try:
            async with aiohttp.ClientSession() as session:
                # DuckDuckGo Instant Answer API
                url = "https://api.duckduckgo.com/"
                params = {
                    "q": query,
                    "format": "json",
                    "no_html": "1",
                    "skip_disambig": "1"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"DuckDuckGo API error: {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    results = []
                    
                    # Add instant answer if available
                    if data.get("Abstract"):
                        results.append(WebSearchResult(
                            title=data.get("AbstractSource", "DuckDuckGo"),
                            url=data.get("AbstractURL", ""),
                            snippet=data.get("Abstract", ""),
                            source="duckduckgo_instant",
                            timestamp=datetime.now().isoformat()
                        ))
                    
                    # Add related topics
                    for topic in data.get("RelatedTopics", [])[:max_results-1]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append(WebSearchResult(
                                title=topic.get("FirstURL", "").split("/")[-1] if topic.get("FirstURL") else "Related Topic",
                                url=topic.get("FirstURL", ""),
                                snippet=topic.get("Text", ""),
                                source="duckduckgo_related",
                                timestamp=datetime.now().isoformat()
                            ))
                    
                    return results[:max_results]
                    
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []

class SerperProvider(WebSearchProvider):
    """Serper.dev search provider (requires API key)."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
    async def search(self, query: str, max_results: int) -> List[WebSearchResult]:
        """Search using Serper.dev API."""
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": max_results
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Serper API error: {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    results = []
                    for item in data.get("organic", []):
                        results.append(WebSearchResult(
                            title=item.get("title", ""),
                            url=item.get("link", ""),
                            snippet=item.get("snippet", ""),
                            source="serper",
                            timestamp=datetime.now().isoformat()
                        ))
                    
                    return results[:max_results]
                    
        except Exception as e:
            logger.error(f"Serper search failed: {e}")
            return []

class PerplexityProvider(WebSearchProvider):
    """Perplexity search provider using their AI-powered search."""
    
    def __init__(self):
        self.provider_factory = LLMProviderFactory()
    
    async def search(self, query: str, max_results: int) -> List[WebSearchResult]:
        """Search using Perplexity API."""
        try:
            # Check if Perplexity is configured
            if ProviderType.PERPLEXITY not in self.provider_factory.get_configured_providers():
                logger.warning("Perplexity not configured, falling back to DuckDuckGo")
                return await DuckDuckGoProvider().search(query, max_results)
            
            # Use Perplexity for search
            provider = self.provider_factory.create_provider(ProviderType.PERPLEXITY)
            
            # Perform search with Perplexity
            search_result = await provider.search(
                query=query,
                model="sonar-pro-online",  # Use online model for search
                max_tokens=1000
            )
            
            # Create result from Perplexity response
            results = []
            if search_result.get("text"):
                results.append(WebSearchResult(
                    title="Perplexity AI Search",
                    url="https://perplexity.ai",
                    snippet=search_result["text"][:500] + "..." if len(search_result["text"]) > 500 else search_result["text"],
                    source="perplexity_ai",
                    timestamp=datetime.now().isoformat()
                ))
            
            # If we don't have enough results, fall back to DuckDuckGo
            if len(results) < max_results:
                duckduckgo_results = await DuckDuckGoProvider().search(query, max_results - len(results))
                results.extend(duckduckgo_results)
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Perplexity search failed: {e}")
            # Fall back to DuckDuckGo
            return await DuckDuckGoProvider().search(query, max_results)

# Initialize search providers
search_providers = {
    "duckduckgo": DuckDuckGoProvider(),
    "perplexity": PerplexityProvider(),
    # "serper": SerperProvider(api_key="your_api_key_here")  # Uncomment and add API key
}

@router.post("/search", response_model=WebSearchResponse, responses={
    200: {
        "description": "Web search results",
        "content": {
            "application/json": {
                "example": {
                    "query": "najnowsze trendy AI",
                    "results": [
                        {
                            "title": "Perplexity AI Search",
                            "url": "https://perplexity.ai",
                            "snippet": "Perplexity AI to nowoczesny silnik wyszukiwania...",
                            "source": "perplexity_ai",
                            "timestamp": "2025-06-01T12:00:00"
                        }
                    ],
                    "total_results": 1,
                    "search_engine": "perplexity",
                    "search_time": 0.42
                }
            }
        }
    }
})
async def web_search(request: WebSearchRequest):
    """
    Perform web search to get current information.
    """
    start_time = datetime.now()
    
    try:
        # Validate search engine
        if request.search_engine not in search_providers:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported search engine: {request.search_engine}. Available: {list(search_providers.keys())}"
            )
        
        # Get provider and perform search
        provider = search_providers[request.search_engine]
        results = await provider.search(request.query, request.max_results)
        
        search_time = (datetime.now() - start_time).total_seconds()
        
        response = WebSearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_engine=request.search_engine,
            search_time=search_time
        )
        
        logger.info(f"Web search completed in {search_time:.2f}s for query: {request.query}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Web search failed: {str(e)}")

@router.get("/providers")
async def get_search_providers():
    """Get available search providers."""
    return {
        "providers": list(search_providers.keys()),
        "default": "duckduckgo"
    }

@router.get("/health")
async def health_check():
    """Health check for web search service."""
    return {
        "status": "healthy",
        "providers": len(search_providers),
        "timestamp": datetime.now().isoformat()
    } 