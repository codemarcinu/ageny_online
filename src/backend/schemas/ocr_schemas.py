from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class OCRRequest(BaseModel):
    """Request model for OCR text extraction."""
    image_data: str = Field(..., description="Base64 encoded image data")
    provider: Optional[str] = Field(None, description="OCR provider to use (mistral, azure, google)")

class OCRResponse(BaseModel):
    """Response model for OCR text extraction."""
    text: str = Field(..., description="Extracted text from image")
    confidence: Optional[float] = Field(None, description="Confidence score (0-1)")
    provider: str = Field(..., description="Provider used for OCR")
    processing_time: float = Field(..., description="Processing time in seconds")
    cost: Optional[float] = Field(None, description="Cost in USD")

class BatchImageData(BaseModel):
    """Model for batch image data."""
    filename: str = Field(..., description="Original filename")
    data: str = Field(..., description="Base64 encoded image data")

class BatchOCRRequest(BaseModel):
    """Request model for batch OCR processing."""
    images: List[BatchImageData] = Field(..., description="List of images to process")
    provider: Optional[str] = Field(None, description="OCR provider to use")

class BatchOCRResponse(BaseModel):
    """Response model for batch OCR processing."""
    results: List[OCRResponse] = Field(..., description="OCR results for each image")
    total_processing_time: float = Field(..., description="Total processing time in seconds")
    total_cost: Optional[float] = Field(None, description="Total cost in USD")
    provider: str = Field(..., description="Provider used for OCR")

class ProviderInfo(BaseModel):
    """Information about an OCR provider."""
    name: str = Field(..., description="Provider name")
    status: str = Field(..., description="Provider status (available, unavailable)")
    capabilities: List[str] = Field(..., description="List of supported capabilities")

class OCRHealthResponse(BaseModel):
    """Health check response for OCR services."""
    status: str = Field(..., description="Overall health status")
    providers: Dict[str, str] = Field(..., description="Health status of each provider")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp") 