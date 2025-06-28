"""
OCR service for Ageny Online.
Zapewnia logikę biznesową OCR z pełną separacją.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.ocr_result import OCRResult
from backend.core.ocr_providers import ocr_provider_factory
from backend.exceptions.ocr import OCRError, OCRProviderError

logger = logging.getLogger(__name__)


class OCRService:
    """Service for OCR operations."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def extract_text(
        self, 
        image_bytes: bytes, 
        user_id: Optional[int] = None,
        session_id: str = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract text from image using OCR.

        Args:
            image_bytes: Image bytes to process
            user_id: User ID (optional)
            session_id: Session ID
            provider: OCR provider to use
            model: Specific model to use
            prompt: Custom prompt for OCR

        Returns:
            Dictionary with OCR results

        Raises:
            OCRError: If OCR processing fails
        """
        try:
            # Get best provider if not specified
            if not provider:
                provider_type = ocr_provider_factory.get_best_provider()
                if not provider_type:
                    raise OCRError("No OCR providers configured")
                provider = provider_type.value

            # Create provider instance
            ocr_provider = ocr_provider_factory.create_provider(provider_type)

            # Extract text
            result = await ocr_provider.extract_text(
                image_bytes=image_bytes,
                model=model,
                prompt=prompt
            )

            # Store result in database
            ocr_record = OCRResult(
                user_id=user_id,
                session_id=session_id or "unknown",
                provider_used=provider,
                model_used=result.get("model_used", ""),
                extracted_text=result["text"],
                confidence=result["confidence"],
                tokens_used=result.get("tokens_used"),
                cost=result.get("cost"),
                image_size_bytes=len(image_bytes),
                processing_time=result.get("processing_time"),
                prompt_used=prompt,
                metadata=result.get("metadata", {})
            )

            self.db_session.add(ocr_record)
            await self.db_session.commit()
            await self.db_session.refresh(ocr_record)

            logger.info(
                f"OCR text extraction completed: provider={provider}, "
                f"text_length={len(result['text'])}, cost={result.get('cost')}"
            )

            return result

        except Exception as e:
            logger.error(f"OCR text extraction failed: {e}")
            await self.db_session.rollback()
            raise OCRError(f"OCR processing failed: {e}")

    async def extract_text_batch(
        self, 
        images: List[bytes], 
        user_id: Optional[int] = None,
        session_id: str = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract text from multiple images.

        Args:
            images: List of image bytes to process
            user_id: User ID (optional)
            session_id: Session ID
            provider: OCR provider to use
            model: Specific model to use
            prompt: Custom prompt for OCR

        Returns:
            List of dictionaries with OCR results

        Raises:
            OCRError: If OCR processing fails
        """
        try:
            # Get best provider if not specified
            if not provider:
                provider_type = ocr_provider_factory.get_best_provider()
                if not provider_type:
                    raise OCRError("No OCR providers configured")
                provider = provider_type.value

            # Create provider instance
            ocr_provider = ocr_provider_factory.create_provider(provider_type)

            # Extract text from all images
            results = await ocr_provider.extract_text_batch(
                images=images,
                model=model,
                prompt=prompt
            )

            # Store results in database
            ocr_records = []
            for i, result in enumerate(results):
                if "error" not in result:
                    ocr_record = OCRResult(
                        user_id=user_id,
                        session_id=session_id or "unknown",
                        provider_used=provider,
                        model_used=result.get("model_used", ""),
                        extracted_text=result["text"],
                        confidence=result["confidence"],
                        tokens_used=result.get("tokens_used"),
                        cost=result.get("cost"),
                        image_size_bytes=len(images[i]),
                        processing_time=result.get("processing_time"),
                        prompt_used=prompt,
                        metadata=result.get("metadata", {})
                    )
                    ocr_records.append(ocr_record)

            if ocr_records:
                self.db_session.add_all(ocr_records)
                await self.db_session.commit()

            logger.info(
                f"OCR batch extraction completed: provider={provider}, "
                f"images={len(images)}, successful={len([r for r in results if 'error' not in r])}"
            )

            return results

        except Exception as e:
            logger.error(f"OCR batch extraction failed: {e}")
            await self.db_session.rollback()
            raise OCRError(f"OCR batch processing failed: {e}")

    async def get_ocr_history(
        self, 
        user_id: Optional[int] = None, 
        session_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[OCRResult]:
        """Get OCR processing history.

        Args:
            user_id: Filter by user ID (optional)
            session_id: Filter by session ID (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of OCR result instances
        """
        query = select(OCRResult)
        
        if user_id:
            query = query.where(OCRResult.user_id == user_id)
        if session_id:
            query = query.where(OCRResult.session_id == session_id)
        
        result = await self.db_session.execute(
            query.order_by(OCRResult.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_ocr_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get OCR processing statistics.

        Args:
            user_id: Filter by user ID (optional)

        Returns:
            Dictionary with OCR statistics
        """
        query = select(OCRResult)
        if user_id:
            query = query.where(OCRResult.user_id == user_id)
        
        result = await self.db_session.execute(query)
        records = result.scalars().all()
        
        if not records:
            return {
                "total_requests": 0,
                "total_cost": 0.0,
                "total_tokens": 0,
                "average_confidence": 0.0,
                "providers_used": {}
            }
        
        total_cost = sum(float(r.cost or 0) for r in records)
        total_tokens = sum(r.tokens_used or 0 for r in records)
        average_confidence = sum(r.confidence or 0 for r in records) / len(records)
        
        providers_used = {}
        for record in records:
            provider = record.provider_used
            if provider not in providers_used:
                providers_used[provider] = 0
            providers_used[provider] += 1
        
        return {
            "total_requests": len(records),
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "average_confidence": average_confidence,
            "providers_used": providers_used
        } 