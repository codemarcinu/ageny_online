"""
Mistral AI Vision OCR Provider.
Zapewnia integrację z Mistral AI Vision API dla OCR operations.
"""

import base64
import logging
from typing import Any, Dict, List, Optional, Union

import httpx
from pydantic import BaseModel

from backend.config import settings

logger = logging.getLogger(__name__)


class MistralVisionConfig(BaseModel):
    """Configuration for Mistral Vision provider"""
    
    model_name: str
    max_tokens: int
    temperature: float
    cost_per_1k: float
    supports_streaming: bool = False
    supports_ocr: bool = True


class MistralVisionOCR:
    """
    Mistral AI Vision OCR Provider.
    Zapewnia integrację z Mistral AI Vision API dla OCR operations.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize Mistral Vision provider"""
        self.api_key = api_key or settings.MISTRAL_API_KEY
        if not self.api_key:
            raise ValueError("Mistral API key is required")
        
        self.base_url = "https://api.mistral.ai/v1"
        self.http_client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": settings.USER_AGENT,
            }
        )
        
        # Model configurations for Mistral Vision
        self.models = {
            "mistral-large-latest": MistralVisionConfig(
                model_name="mistral-large-latest",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k=0.007,
                supports_streaming=False,
                supports_ocr=True,
            ),
            "mistral-medium-latest": MistralVisionConfig(
                model_name="mistral-medium-latest",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k=0.0024,
                supports_streaming=False,
                supports_ocr=True,
            ),
            "mistral-small-latest": MistralVisionConfig(
                model_name="mistral-small-latest",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k=0.0007,
                supports_streaming=False,
                supports_ocr=True,
            ),
        }
        
        # Default model for OCR
        self.default_model = "mistral-large-latest"
        
        logger.info(f"Mistral Vision provider initialized with model: {self.default_model}")

    async def extract_text(
        self, 
        image_bytes: bytes, 
        model: Optional[str] = None,
        prompt: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Extract text from image using Mistral Vision API.
        
        Args:
            image_bytes: Image bytes to process
            model: Model to use (defaults to configured model)
            prompt: Custom prompt for OCR (optional)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with extracted text and metadata
            
        Raises:
            Exception: If API call fails
        """
        try:
            model_name = model or self.default_model
            model_config = self.models.get(model_name)
            
            if not model_config:
                logger.warning(f"Model {model_name} not found, using default")
                model_name = self.default_model
                model_config = self.models.get(model_name)
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Default OCR prompt if not provided
            if not prompt:
                prompt = """Please extract all text from this image. Return the text exactly as it appears, maintaining the original formatting and structure. If there are multiple lines, separate them with newlines. If there are tables or structured data, preserve the layout as much as possible."""
            
            # Prepare request payload
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": model_config.max_tokens if model_config else 4096,
                "temperature": model_config.temperature if model_config else 0.1,
                **kwargs
            }
            
            logger.debug(f"Mistral Vision OCR request: model={model_name}, image_size={len(image_bytes)}")
            
            # Make API request
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            if response.status_code != 200:
                error_msg = f"Mistral Vision API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            
            # Extract text from response
            extracted_text = response_data["choices"][0]["message"]["content"]
            
            # Calculate usage
            usage = response_data.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)
            cost = self.calculate_cost(model_name, tokens_used)
            
            return {
                "text": extracted_text,
                "confidence": 0.95,  # Mistral doesn't provide confidence scores
                "model_used": model_name,
                "tokens_used": tokens_used,
                "cost": cost,
                "metadata": {
                    "provider": "mistral_vision",
                    "model": model_name,
                    "image_size_bytes": len(image_bytes),
                    "prompt_used": prompt,
                }
            }
            
        except Exception as e:
            logger.error(f"Mistral Vision OCR error: {e}")
            raise Exception(f"Mistral Vision OCR failed: {e}")

    async def extract_text_batch(
        self, 
        images: List[bytes], 
        model: Optional[str] = None,
        prompt: Optional[str] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Extract text from multiple images using Mistral Vision API.
        
        Args:
            images: List of image bytes to process
            model: Model to use (defaults to configured model)
            prompt: Custom prompt for OCR (optional)
            **kwargs: Additional parameters
            
        Returns:
            List of dictionaries with extracted text and metadata
            
        Raises:
            Exception: If API call fails
        """
        results = []
        
        for i, image_bytes in enumerate(images):
            try:
                result = await self.extract_text(image_bytes, model, prompt, **kwargs)
                result["image_index"] = i
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing image {i}: {e}")
                results.append({
                    "text": "",
                    "confidence": 0,
                    "error": str(e),
                    "image_index": i,
                    "metadata": {"provider": "mistral_vision", "error": str(e)}
                })
        
        return results

    async def analyze_image(
        self, 
        image_bytes: bytes, 
        analysis_prompt: str,
        model: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Analyze image content using Mistral Vision API.
        
        Args:
            image_bytes: Image bytes to analyze
            analysis_prompt: Prompt for image analysis
            model: Model to use (defaults to configured model)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with analysis results
            
        Raises:
            Exception: If API call fails
        """
        try:
            model_name = model or self.default_model
            model_config = self.models.get(model_name)
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Prepare request payload
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": analysis_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": model_config.max_tokens if model_config else 4096,
                "temperature": model_config.temperature if model_config else 0.1,
                **kwargs
            }
            
            logger.debug(f"Mistral Vision analysis request: model={model_name}")
            
            # Make API request
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            if response.status_code != 200:
                error_msg = f"Mistral Vision API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            
            # Extract analysis from response
            analysis = response_data["choices"][0]["message"]["content"]
            
            # Calculate usage
            usage = response_data.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)
            cost = self.calculate_cost(model_name, tokens_used)
            
            return {
                "analysis": analysis,
                "model_used": model_name,
                "tokens_used": tokens_used,
                "cost": cost,
                "metadata": {
                    "provider": "mistral_vision",
                    "model": model_name,
                    "image_size_bytes": len(image_bytes),
                    "prompt_used": analysis_prompt,
                }
            }
            
        except Exception as e:
            logger.error(f"Mistral Vision analysis error: {e}")
            raise Exception(f"Mistral Vision analysis failed: {e}")

    def get_model_info(self, model_name: str) -> Optional[MistralVisionConfig]:
        """Get information about a specific model"""
        return self.models.get(model_name)

    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(self.models.keys())

    def calculate_cost(self, model_name: str, tokens: int) -> float:
        """Calculate cost for token usage"""
        model_config = self.models.get(model_name)
        if not model_config:
            return 0.0
        return (tokens / 1000) * model_config.cost_per_1k

    async def health_check(self) -> Dict[str, Any]:
        """Check if Mistral Vision API is available"""
        try:
            # Try to list models to check API connectivity
            response = await self.http_client.get(f"{self.base_url}/models")
            
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model["id"] for model in models_data.get("data", [])]
                
                return {
                    "status": "healthy",
                    "models_count": len(available_models),
                    "available_models": available_models,
                    "provider": "mistral_vision",
                    "default_model": self.default_model,
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"API returned status {response.status_code}",
                    "provider": "mistral_vision",
                }
                
        except Exception as e:
            logger.error(f"Mistral Vision health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": "mistral_vision",
            }

    async def close(self) -> None:
        """Close HTTP client"""
        await self.http_client.aclose() 