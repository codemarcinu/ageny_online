import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import httpx
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a specific Mistral model."""
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    context_length: int

class MistralProvider:
    """Mistral AI API provider for chat completions and embeddings."""
    
    def __init__(self, api_key: str):
        """
        Initialize Mistral provider.
        
        Args:
            api_key: Mistral API key
        """
        if not api_key:
            raise ValueError("Mistral API key is required")
        
        self.client = MistralClient(api_key=api_key)
        
        # Model configurations with costs (as of 2024)
        self.models = {
            "mistral-large-latest": ModelConfig(
                max_tokens=32768,
                cost_per_1k_input=0.007,
                cost_per_1k_output=0.024,
                context_length=32768
            ),
            "mistral-medium-latest": ModelConfig(
                max_tokens=32768,
                cost_per_1k_input=0.0027,
                cost_per_1k_output=0.0081,
                context_length=32768
            ),
            "mistral-small-latest": ModelConfig(
                max_tokens=32768,
                cost_per_1k_input=0.00014,
                cost_per_1k_output=0.00042,
                context_length=32768
            ),
            "open-mistral-7b": ModelConfig(
                max_tokens=32768,
                cost_per_1k_input=0.00014,
                cost_per_1k_output=0.00042,
                context_length=32768
            )
        }
        
        self.default_model = "mistral-small-latest"
        logger.info(f"Mistral provider initialized with default model: {self.default_model}")
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to self.default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters for Mistral API
            
        Returns:
            Dictionary containing response text, usage, and cost
        """
        model = model or self.default_model
        
        if model not in self.models:
            raise ValueError(f"Unsupported model: {model}")
        
        model_config = self.models[model]
        max_tokens = max_tokens or model_config.max_tokens
        
        try:
            logger.debug(f"Generating chat completion with model: {model}")
            
            # Convert messages to Mistral format
            mistral_messages = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in messages
            ]
            
            response = await asyncio.to_thread(
                self.client.chat,
                model=model,
                messages=mistral_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Calculate costs
            usage = response.usage
            input_cost = (usage.prompt_tokens / 1000) * model_config.cost_per_1k_input
            output_cost = (usage.completion_tokens / 1000) * model_config.cost_per_1k_output
            total_cost = input_cost + output_cost
            
            result = {
                "text": response.choices[0].message.content,
                "model": model,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "cost": {
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                    "total_cost": total_cost
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(f"Chat completion successful. Cost: ${total_cost:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in Mistral chat completion: {e}")
            raise
    
    async def embed(
        self, 
        texts: Union[str, List[str]], 
        model: str = "mistral-embed"
    ) -> Dict[str, Any]:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text string or list of text strings
            model: Embedding model to use
            
        Returns:
            Dictionary containing embeddings and usage info
        """
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            logger.debug(f"Generating embeddings for {len(texts)} texts")
            
            response = await asyncio.to_thread(
                self.client.embeddings,
                model=model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            usage = response.usage
            
            # Calculate cost (mistral-embed: $0.0001 per 1M tokens)
            cost_per_1m = 0.0001
            total_cost = (usage.total_tokens / 1_000_000) * cost_per_1m
            
            result = {
                "embeddings": embeddings,
                "model": model,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "total_tokens": usage.total_tokens
                },
                "cost": total_cost
            }
            
            logger.info(f"Embeddings generated successfully. Cost: ${total_cost:.6f}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return list(self.models.keys())
    
    def get_model_config(self, model: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model."""
        return self.models.get(model) 