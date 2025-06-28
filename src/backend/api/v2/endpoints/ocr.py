"""
OCR API endpoints.
Zapewnia endpointy do przetwarzania OCR z różnymi providerami.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.core.ocr_providers import ocr_provider_factory, OCRProviderType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["OCR"])


class OCRResponse(BaseModel):
    """OCR response model"""
    text: str
    confidence: float
    provider: str
    model_used: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    metadata: dict


class OCRBatchResponse(BaseModel):
    """OCR batch response model"""
    results: List[OCRResponse]
    total_cost: float
    total_tokens: int


@router.post("/extract-text", response_model=OCRResponse)
async def extract_text(
    file: UploadFile = File(...),
    provider: Optional[str] = None,
    model: Optional[str] = None,
    prompt: Optional[str] = None,
):
    """
    Extract text from image using OCR.
    
    Args:
        file: Image file to process
        provider: OCR provider to use (mistral_vision, azure_vision, google_vision)
        model: Specific model to use
        prompt: Custom prompt for OCR
        
    Returns:
        Extracted text and metadata
    """
    try:
        # Read file content
        file_bytes = await file.read()
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are supported"
            )
        
        # Determine provider
        if provider:
            try:
                provider_type = OCRProviderType(provider)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported provider: {provider}. Available: {[p.value for p in OCRProviderType]}"
                )
        else:
            # Use best available provider
            provider_type = ocr_provider_factory.get_best_provider()
            if not provider_type:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No OCR providers configured"
                )
        
        # Create provider instance
        ocr_provider = ocr_provider_factory.create_provider(provider_type)
        
        # Extract text
        result = await ocr_provider.extract_text(
            file_bytes,
            model=model,
            prompt=prompt
        )
        
        logger.info(
            f"OCR text extraction completed: provider={provider_type.value}, "
            f"text_length={len(result['text'])}, confidence={result['confidence']}"
        )
        
        return OCRResponse(
            text=result["text"],
            confidence=result["confidence"],
            provider=provider_type.value,
            model_used=result.get("model_used", ""),
            tokens_used=result.get("tokens_used"),
            cost=result.get("cost"),
            metadata=result.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR text extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}"
        )


@router.post("/extract-text-batch", response_model=OCRBatchResponse)
async def extract_text_batch(
    files: List[UploadFile] = File(...),
    provider: Optional[str] = None,
    model: Optional[str] = None,
    prompt: Optional[str] = None,
):
    """
    Extract text from multiple images using OCR.
    
    Args:
        files: List of image files to process
        provider: OCR provider to use
        model: Specific model to use
        prompt: Custom prompt for OCR
        
    Returns:
        List of extracted text results
    """
    try:
        if len(files) > 10:  # Limit batch size
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files allowed per batch"
            )
        
        # Validate all files
        file_bytes_list = []
        for file in files:
            if not file.content_type or not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Only image files are supported. File {file.filename} is not an image."
                )
            file_bytes = await file.read()
            file_bytes_list.append(file_bytes)
        
        # Determine provider
        if provider:
            try:
                provider_type = OCRProviderType(provider)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported provider: {provider}. Available: {[p.value for p in OCRProviderType]}"
                )
        else:
            provider_type = ocr_provider_factory.get_best_provider()
            if not provider_type:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No OCR providers configured"
                )
        
        # Create provider instance
        ocr_provider = ocr_provider_factory.create_provider(provider_type)
        
        # Extract text from all images
        results = await ocr_provider.extract_text_batch(
            file_bytes_list,
            model=model,
            prompt=prompt
        )
        
        # Convert to response format
        ocr_responses = []
        total_cost = 0.0
        total_tokens = 0
        
        for i, result in enumerate(results):
            if "error" in result:
                # Handle error case
                ocr_responses.append(OCRResponse(
                    text="",
                    confidence=0.0,
                    provider=provider_type.value,
                    model_used="",
                    metadata={"error": result["error"], "image_index": i}
                ))
            else:
                ocr_responses.append(OCRResponse(
                    text=result["text"],
                    confidence=result["confidence"],
                    provider=provider_type.value,
                    model_used=result.get("model_used", ""),
                    tokens_used=result.get("tokens_used"),
                    cost=result.get("cost"),
                    metadata=result.get("metadata", {})
                ))
                
                total_cost += result.get("cost", 0.0)
                total_tokens += result.get("tokens_used", 0)
        
        logger.info(
            f"OCR batch extraction completed: provider={provider_type.value}, "
            f"files={len(files)}, total_cost=${total_cost:.4f}"
        )
        
        return OCRBatchResponse(
            results=ocr_responses,
            total_cost=total_cost,
            total_tokens=total_tokens
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR batch extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR batch processing failed: {str(e)}"
        )


@router.get("/providers")
async def get_available_providers():
    """Get list of available OCR providers and their status"""
    try:
        available_providers = ocr_provider_factory.get_available_providers()
        configured_providers = ocr_provider_factory.get_configured_providers()
        
        providers_info = {}
        for provider_type in available_providers:
            providers_info[provider_type.value] = {
                "available": True,
                "configured": provider_type in configured_providers,
                "priority": ocr_provider_factory.get_provider_priority(provider_type)
            }
        
        best_provider = ocr_provider_factory.get_best_provider()
        
        return {
            "providers": providers_info,
            "best_provider": best_provider.value if best_provider else None,
            "configured_count": len(configured_providers)
        }
        
    except Exception as e:
        logger.error(f"Error getting providers info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get providers info: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check health of all OCR providers"""
    try:
        health_results = await ocr_provider_factory.health_check_all()
        return {
            "status": "healthy" if any(r.get("status") == "healthy" for r in health_results.values()) else "unhealthy",
            "providers": health_results
        }
        
    except Exception as e:
        logger.error(f"OCR health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        ) 