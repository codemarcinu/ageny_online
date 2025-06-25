from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import base64
from io import BytesIO
from PIL import Image

from src.backend.core.ocr_providers.ocr_factory import OCRProviderFactory
from src.backend.schemas.ocr_schemas import (
    OCRRequest,
    OCRResponse,
    BatchOCRRequest,
    BatchOCRResponse,
    ProviderInfo
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/extract", response_model=OCRResponse)
async def extract_text(
    request: Request,
    file: UploadFile = File(...),
    provider: Optional[str] = None
):
    """
    Extract text from uploaded image using OCR.
    
    Args:
        file: Image file to process
        provider: Optional OCR provider name (mistral, azure, google)
    
    Returns:
        OCRResponse with extracted text and metadata
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and validate image
        image_data = await file.read()
        try:
            image = Image.open(BytesIO(image_data))
            image.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Create OCR request
        ocr_request = OCRRequest(
            image_data=image_base64,
            provider=provider
        )
        
        # Process with OCR factory
        ocr_factory = OCRProviderFactory()
        result = await ocr_factory.extract_text(ocr_request)
        
        return OCRResponse(
            text=result.text,
            confidence=result.confidence,
            provider=result.provider,
            processing_time=result.processing_time,
            cost=result.cost
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise HTTPException(status_code=500, detail="OCR extraction failed")

@router.post("/batch", response_model=BatchOCRResponse)
async def batch_extract_text(
    request: Request,
    files: List[UploadFile] = File(...),
    provider: Optional[str] = None
):
    """
    Extract text from multiple images using OCR.
    
    Args:
        files: List of image files to process
        provider: Optional OCR provider name
    
    Returns:
        BatchOCRResponse with results for all images
    """
    try:
        if len(files) > 10:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 10 files per batch")
        
        # Validate all files
        image_data_list = []
        for file in files:
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} must be an image")
            
            data = await file.read()
            try:
                image = Image.open(BytesIO(data))
                image.verify()
            except Exception:
                raise HTTPException(status_code=400, detail=f"Invalid image file: {file.filename}")
            
            image_data_list.append({
                'filename': file.filename,
                'data': base64.b64encode(data).decode('utf-8')
            })
        
        # Create batch request
        batch_request = BatchOCRRequest(
            images=image_data_list,
            provider=provider
        )
        
        # Process with OCR factory
        ocr_factory = OCRProviderFactory()
        result = await ocr_factory.batch_extract_text(batch_request)
        
        return BatchOCRResponse(
            results=result.results,
            total_processing_time=result.total_processing_time,
            total_cost=result.total_cost,
            provider=result.provider
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch OCR extraction failed: {e}")
        raise HTTPException(status_code=500, detail="Batch OCR extraction failed")

@router.get("/providers", response_model=List[ProviderInfo])
async def get_ocr_providers():
    """
    Get available OCR providers and their capabilities.
    
    Returns:
        List of available OCR providers with their information
    """
    try:
        ocr_factory = OCRProviderFactory()
        providers = ocr_factory.get_available_providers()
        
        provider_info = []
        for provider_name in providers:
            provider_info.append(ProviderInfo(
                name=provider_name,
                status="available",
                capabilities=["text_extraction", "batch_processing"]
            ))
        
        return provider_info
        
    except Exception as e:
        logger.error(f"Failed to get OCR providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get OCR providers")

@router.get("/health")
async def ocr_health_check():
    """
    Health check for OCR services.
    
    Returns:
        Health status of OCR providers
    """
    try:
        ocr_factory = OCRProviderFactory()
        providers = ocr_factory.get_available_providers()
        
        health_status = {}
        for provider_name in providers:
            try:
                # Test provider availability
                health_status[provider_name] = "healthy"
            except Exception:
                health_status[provider_name] = "unhealthy"
        
        return {
            "status": "healthy" if all(status == "healthy" for status in health_status.values()) else "degraded",
            "providers": health_status
        }
        
    except Exception as e:
        logger.error(f"OCR health check failed: {e}")
        raise HTTPException(status_code=500, detail="OCR health check failed") 