import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from google.cloud import vision
from google.cloud.vision_v1 import types

logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    """Result of OCR processing."""
    text: str
    confidence: float
    bounding_boxes: List[Dict[str, Any]]
    language: Optional[str] = None

class GoogleVisionProvider:
    """Google Cloud Vision OCR provider."""
    
    def __init__(self, project_id: str, credentials_path: Optional[str] = None):
        """
        Initialize Google Vision provider.
        
        Args:
            project_id: Google Cloud project ID
            credentials_path: Path to service account credentials (optional)
        """
        if not project_id:
            raise ValueError("Google Cloud project ID is required")
        
        # Initialize Vision client
        if credentials_path:
            self.client = vision.ImageAnnotatorClient.from_service_account_file(credentials_path)
        else:
            # Use default credentials (GOOGLE_APPLICATION_CREDENTIALS env var)
            self.client = vision.ImageAnnotatorClient()
        
        self.project_id = project_id
        
        # Cost per 1000 API calls (as of 2024)
        self.cost_per_1k_calls = 1.50  # USD
        
        logger.info(f"Google Vision provider initialized with project: {project_id}")
    
    async def extract_text(
        self, 
        image_data: bytes,
        language_hints: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract text from image using Google Vision OCR.
        
        Args:
            image_data: Image data as bytes
            language_hints: List of language hints (optional)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing OCR results and cost info
        """
        try:
            logger.debug("Starting Google Vision OCR processing")
            
            # Create image object
            image = types.Image(content=image_data)
            
            # Configure text detection
            config = types.TextDetectionParams(
                language_hints=language_hints or ["en"]
            )
            
            # Create text detection request
            request = types.AnnotateImageRequest(
                image=image,
                features=[types.Feature(type_=types.Feature.Type.TEXT_DETECTION, max_results=kwargs.get('max_results', 10))],
                image_context=types.ImageContext(text_detection_params=config)
            )
            
            # Call Google Vision API
            response = await asyncio.to_thread(
                self.client.annotate_image,
                request
            )
            
            # Process results
            ocr_results = self._process_ocr_result(response)
            
            # Calculate cost (1 call per image)
            cost = self.cost_per_1k_calls / 1000
            
            result = {
                "text": ocr_results.text,
                "confidence": ocr_results.confidence,
                "language": ocr_results.language,
                "bounding_boxes": ocr_results.bounding_boxes,
                "provider": "google_vision",
                "cost": cost,
                "raw_result": response
            }
            
            logger.info(f"Google Vision OCR completed successfully. Cost: ${cost:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in Google Vision OCR: {e}")
            raise
    
    def _process_ocr_result(self, response: types.AnnotateImageResponse) -> OCRResult:
        """
        Process raw OCR result from Google Vision.
        
        Args:
            response: Raw response from Google Vision API
            
        Returns:
            Processed OCR result
        """
        if not response.text_annotations:
            return OCRResult(text="", confidence=0.0, bounding_boxes=[])
        
        # First annotation contains the full text
        full_text_annotation = response.text_annotations[0]
        full_text = full_text_annotation.description
        
        # Process individual text blocks for confidence and bounding boxes
        bounding_boxes = []
        all_confidence = []
        
        for text_annotation in response.text_annotations[1:]:  # Skip first (full text)
            text = text_annotation.description
            confidence = text_annotation.confidence if hasattr(text_annotation, 'confidence') else 0.8
            
            all_confidence.append(confidence)
            
            # Extract bounding box
            if text_annotation.bounding_poly:
                vertices = text_annotation.bounding_poly.vertices
                bbox = {
                    "text": text,
                    "confidence": confidence,
                    "bbox": [
                        {"x": vertex.x, "y": vertex.y} for vertex in vertices
                    ]
                }
                bounding_boxes.append(bbox)
        
        # Calculate overall confidence
        overall_confidence = sum(all_confidence) / len(all_confidence) if all_confidence else 0.8
        
        # Try to detect language from response
        language = None
        if hasattr(response, 'text_annotations') and response.text_annotations:
            # Google Vision doesn't always return language info in OCR
            # You might need to use a separate language detection API
            pass
        
        return OCRResult(
            text=full_text,
            confidence=overall_confidence,
            bounding_boxes=bounding_boxes,
            language=language
        )
    
    async def extract_text_batch(
        self, 
        images: List[bytes],
        language_hints: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Extract text from multiple images.
        
        Args:
            images: List of image data as bytes
            language_hints: List of language hints (optional)
            **kwargs: Additional parameters
            
        Returns:
            List of OCR results
        """
        tasks = [
            self.extract_text(image, language_hints, **kwargs)
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
                    "provider": "google_vision",
                    "cost": 0.0,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language of text using Google Vision.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language detection result
        """
        try:
            # Create document object
            document = types.Document(
                content=text,
                type_=types.Document.Type.PLAIN_TEXT
            )
            
            # Create language detection request
            request = types.AnnotateDocumentRequest(
                document=document,
                features=[types.DocumentFeature(type_=types.DocumentFeature.Type.LANGUAGE_HINTS)]
            )
            
            # Call API
            response = await asyncio.to_thread(
                self.client.document_text_detection,
                document
            )
            
            # Extract language info
            language = response.full_text_annotation.pages[0].property.detected_languages[0].language_code if response.full_text_annotation.pages else "en"
            confidence = response.full_text_annotation.pages[0].property.detected_languages[0].confidence if response.full_text_annotation.pages else 1.0
            
            return {
                "language": language,
                "confidence": confidence,
                "provider": "google_vision"
            }
            
        except Exception as e:
            logger.error(f"Error in language detection: {e}")
            return {
                "language": "en",
                "confidence": 0.0,
                "provider": "google_vision",
                "error": str(e)
            }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return [
            "en", "es", "fr", "de", "it", "pt", "nl", "pl", "ru", "ja", "ko", "zh", "ar", "hi", "th"
        ]
    
    def get_cost_info(self) -> Dict[str, Any]:
        """Get cost information."""
        return {
            "cost_per_1k_calls": self.cost_per_1k_calls,
            "currency": "USD",
            "provider": "google_vision"
        } 