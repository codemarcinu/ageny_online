from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import time
import asyncio

from ....config import get_settings
from ....core.llm_providers.provider_factory import llm_factory, ProviderType, ProviderConfig

logger = logging.getLogger(__name__)

router = APIRouter()

settings = get_settings()

class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    """Chat completion request model."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    model: Optional[str] = Field(None, description="Model to use for completion")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature", ge=0.0, le=2.0)
    provider: Optional[str] = Field(None, description="Specific provider to use")
    stream: bool = Field(False, description="Whether to stream the response")

class ChatResponse(BaseModel):
    """Chat completion response model."""
    text: str
    model: str
    provider: str
    usage: Dict[str, int]
    cost: Dict[str, float]
    finish_reason: str
    response_time: float

class EmbedRequest(BaseModel):
    """Embedding request model."""
    texts: List[str] = Field(..., description="List of texts to embed")
    model: Optional[str] = Field(None, description="Model to use for embedding")

@router.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Generate chat completion using available LLM providers.
    
    This endpoint automatically selects the best available provider based on configuration
    and falls back to alternatives if the primary provider fails.
    """
    start_time = time.time()
    
    try:
        # Convert messages to the format expected by providers
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Validate messages
        if not messages:
            raise HTTPException(status_code=400, detail="At least one message is required")
        
        # Check if specific provider is requested
        if request.provider:
            try:
                provider_type = ProviderType(request.provider)
                provider = llm_factory.get_provider(provider_type)
                
                # Adapt model name for provider if needed
                adapted_model = llm_factory._adapt_model_for_provider(request.model, provider_type)
                
                result = await provider.chat(
                    messages=messages,
                    model=adapted_model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature
                )
                result["provider"] = request.provider
                
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")
            except Exception as e:
                logger.error(f"Provider {request.provider} failed: {e}")
                raise HTTPException(status_code=500, detail=f"Provider {request.provider} failed")
        else:
            # Use fallback mechanism
            result = await llm_factory.chat_with_fallback(
                messages=messages,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Add response time to result
        result["response_time"] = response_time
        
        logger.info(f"Chat completion successful with {result['provider']} in {response_time:.2f}s")
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail="Chat completion failed")

@router.post("/batch")
async def chat_completion_batch(requests: List[ChatRequest]):
    """
    Generate chat completions for multiple requests in batch.
    
    This endpoint processes multiple chat requests concurrently for better performance.
    """
    start_time = time.time()
    
    try:
        # Process requests concurrently
        tasks = []
        for req in requests:
            messages = [{"role": msg.role, "content": msg.content} for msg in req.messages]
            task = llm_factory.chat_with_fallback(
                messages=messages,
                model=req.model,
                max_tokens=req.max_tokens,
                temperature=req.temperature
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Request {i} failed: {result}")
                processed_results.append({
                    "text": "",
                    "model": "",
                    "provider": "",
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                    "cost": {"input_cost": 0.0, "output_cost": 0.0, "total_cost": 0.0},
                    "finish_reason": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        # Calculate total cost and usage
        total_cost = sum(r.get("cost", {}).get("total_cost", 0) for r in processed_results)
        total_tokens = sum(r.get("usage", {}).get("total_tokens", 0) for r in processed_results)
        
        response_time = time.time() - start_time
        
        return {
            "results": processed_results,
            "batch_info": {
                "total_requests": len(requests),
                "successful_requests": len([r for r in processed_results if "error" not in r]),
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "response_time": response_time
            }
        }
        
    except Exception as e:
        logger.error(f"Batch chat completion failed: {e}")
        raise HTTPException(status_code=500, detail="Batch chat completion failed")

@router.get("/models")
async def get_available_models():
    """Get available models from all configured providers."""
    try:
        models = {}
        
        for provider_type in ProviderType:
            try:
                provider = llm_factory.get_provider(provider_type)
                models[provider_type.value] = provider.get_available_models()
            except Exception as e:
                logger.warning(f"Could not get models for {provider_type.value}: {e}")
                models[provider_type.value] = []
        
        return {
            "models": models,
            "default_models": {
                "openai": "gpt-4o-mini",
                "mistral": "mistral-small-latest"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get models")

@router.get("/providers/status")
async def get_provider_status():
    """Get status of all LLM providers."""
    try:
        return {
            "providers": llm_factory.get_provider_status(),
            "available_providers": llm_factory.get_available_providers(),
            "fallback_order": llm_factory._fallback_order
        }
        
    except Exception as e:
        logger.error(f"Failed to get provider status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get provider status")

@router.post("/embed")
async def create_embeddings(request: EmbedRequest):
    """
    Create embeddings for text using available providers.
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="At least one text is required")
        
        result = await llm_factory.embed_with_fallback(
            texts=request.texts,
            model=request.model
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Embedding creation failed: {e}")
        raise HTTPException(status_code=500, detail="Embedding creation failed") 