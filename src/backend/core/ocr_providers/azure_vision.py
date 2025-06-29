import asyncio
import logging
import base64
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    """Result of OCR processing."""
    text: str
    confidence: float
    bounding_boxes: List[Dict[str, Any]]
    language: Optional[str] = None

class AzureVisionProvider:
    """Azure Computer Vision OCR provider."""
    
    def __init__(self, api_key: str, endpoint: str, region: Optional[str] = None):
        """
        Initialize Azure Vision provider.
        
        Args:
            api_key: Azure Vision API key
            endpoint: Azure Vision endpoint URL
            region: Azure region (optional)
        """
        if not api_key or not endpoint:
            raise ValueError("Azure Vision API key and endpoint are required")
        
        self.client = ComputerVisionClient(
            endpoint=endpoint,
            credentials=CognitiveServicesCredentials(api_key)
        )
        self.region = region
        
        # Cost per 1000 transactions (as of 2024)
        self.cost_per_1k_transactions = 1.50  # USD
        
        logger.info(f"Azure Vision provider initialized with endpoint: {endpoint}")
    
    async def extract_text(
        self, 
        image_data: bytes,
        language: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract text from image using Azure Vision OCR.
        
        Args:
            image_data: Image data as bytes
            language: Language hint (optional)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing OCR results and cost info
        """
        try:
            logger.debug("Starting Azure Vision OCR processing")
            
            # Convert image to base64 for API call
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Call Azure Vision API
            result = await asyncio.to_thread(
                self.client.read_in_stream,
                image_data,
                language=language,
                **kwargs
            )
            
            # Get operation location for async processing
            operation_location = result.headers.get("Operation-Location")
            if not operation_location:
                raise RuntimeError("No operation location returned from Azure Vision")
            
            # Extract operation ID from location
            operation_id = operation_location.split("/")[-1]
            
            # Wait for operation to complete
            result = await self._wait_for_operation(operation_id)
            
            # Process results
            ocr_results = self._process_ocr_result(result)
            
            # Calculate cost (1 transaction per image)
            cost = self.cost_per_1k_transactions / 1000
            
            response = {
                "text": ocr_results.text,
                "confidence": ocr_results.confidence,
                "language": ocr_results.language,
                "bounding_boxes": ocr_results.bounding_boxes,
                "provider": "azure_vision",
                "cost": cost,
                "raw_result": result
            }
            
            logger.info(f"Azure Vision OCR completed successfully. Cost: ${cost:.4f}")
            return response
            
        except Exception as e:
            logger.error(f"Error in Azure Vision OCR: {e}")
            raise
    
    async def _wait_for_operation(self, operation_id: str, max_wait_time: int = 60) -> Any:
        """
        Wait for OCR operation to complete.
        
        Args:
            operation_id: Operation ID to wait for
            max_wait_time: Maximum wait time in seconds
            
        Returns:
            Operation result
        """
        import time
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            result = await asyncio.to_thread(
                self.client.get_read_result,
                operation_id
            )
            
            if result.status in [OperationStatusCodes.succeeded, OperationStatusCodes.failed]:
                if result.status == OperationStatusCodes.failed:
                    raise RuntimeError("OCR operation failed")
                return result
            
            # Wait before next check
            await asyncio.sleep(1)
        
        raise TimeoutError("OCR operation timed out")
    
    def _process_ocr_result(self, result: Any) -> OCRResult:
        """
        Process raw OCR result from Azure Vision.
        
        Args:
            result: Raw result from Azure Vision API
            
        Returns:
            Processed OCR result
        """
        if not result.analyze_result or not result.analyze_result.read_results:
            return OCRResult(text="", confidence=0.0, bounding_boxes=[])
        
        read_results = result.analyze_result.read_results
        
        # Extract text and confidence
        all_text = []
        all_confidence = []
        bounding_boxes = []
        
        for page in read_results:
            for line in page.lines:
                line_text = " ".join([word.text for word in line.words])
                all_text.append(line_text)
                
                # Calculate average confidence for line
                if line.words:
                    line_confidence = sum(word.confidence for word in line.words) / len(line.words)
                    all_confidence.append(line_confidence)
                
                # Extract bounding box
                if hasattr(line, 'bounding_box') and line.bounding_box:
                    bounding_boxes.append({
                        "text": line_text,
                        "confidence": line_confidence if line.words else 0.0,
                        "bbox": line.bounding_box
                    })
        
        # Combine all text
        full_text = " ".join(all_text)
        
        # Calculate overall confidence
        overall_confidence = sum(all_confidence) / len(all_confidence) if all_confidence else 0.0
        
        return OCRResult(
            text=full_text,
            confidence=overall_confidence,
            bounding_boxes=bounding_boxes,
            language=result.analyze_result.language if hasattr(result.analyze_result, 'language') else None
        )
    
    async def extract_text_batch(
        self, 
        images: List[bytes],
        language: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Extract text from multiple images.
        
        Args:
            images: List of image data as bytes
            language: Language hint (optional)
            **kwargs: Additional parameters
            
        Returns:
            List of OCR results
        """
        tasks = [
            self.extract_text(image, language, **kwargs)
            for image in images
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process image {i}: {result}")
                processed_results.append({
                    "text": "",
                    "confidence": 0.0,
                    "language": None,
                    "bounding_boxes": [],
                    "provider": "azure_vision",
                    "cost": 0.0,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return [
            "en", "es", "fr", "de", "it", "pt", "nl", "pl", "ru", "ja", "ko", "zh-Hans", "zh-Hant"
        ]
    
    def get_cost_info(self) -> Dict[str, Any]:
        """Get cost information."""
        return {
            "cost_per_1k_transactions": self.cost_per_1k_transactions,
            "currency": "USD",
            "provider": "azure_vision"
        } 