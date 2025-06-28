# Mistral AI Vision OCR Guide

## Overview

Mistral AI Vision OCR provides advanced optical character recognition capabilities through the Mistral AI API. This guide covers integration, usage, and best practices for implementing Mistral Vision OCR in the Ageny Online application.

## Features

- **High Accuracy**: Advanced vision models for text extraction
- **Multi-language Support**: Supports multiple languages including Polish
- **Batch Processing**: Process multiple images efficiently
- **Cost Effective**: Competitive pricing compared to other OCR providers
- **Real-time Processing**: Fast response times for immediate results

## Setup

### 1. Get Mistral API Key

1. Visit [Mistral AI Console](https://console.mistral.ai/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the API key for configuration

### 2. Configure Environment

Add your Mistral API key to the `.env.online` file:

```bash
# Mistral AI Configuration
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_BASE_URL=https://api.mistral.ai/v1
MISTRAL_CHAT_MODEL=mistral-large-latest
MISTRAL_VISION_MODEL=mistral-large-latest
MISTRAL_MAX_TOKENS=4096
MISTRAL_TEMPERATURE=0.1
```

### 3. Available Models

| Model | Description | Max Tokens | Cost (Input/Output) | Vision Support |
|-------|-------------|------------|-------------------|----------------|
| `mistral-large-latest` | Latest large model | 4096 | $0.007/$0.024 | ✅ |
| `mistral-medium-latest` | Latest medium model | 4096 | $0.0024/$0.0072 | ✅ |
| `mistral-small-latest` | Latest small model | 4096 | $0.0007/$0.0024 | ✅ |

## API Usage

### Single Image OCR

```python
from backend.core.ocr_providers import MistralVisionOCR

# Initialize provider
ocr = MistralVisionOCR(api_key="your_api_key")

# Extract text from image
with open("receipt.jpg", "rb") as f:
    image_bytes = f.read()

result = await ocr.extract_text(
    image_bytes=image_bytes,
    model="mistral-large-latest",
    prompt="Extract all text from this receipt, maintaining the original formatting."
)

print(f"Extracted text: {result['text']}")
print(f"Confidence: {result['confidence']}")
print(f"Cost: ${result['cost']:.4f}")
```

### Batch Processing

```python
# Process multiple images
images = [image1_bytes, image2_bytes, image3_bytes]

results = await ocr.extract_text_batch(
    images=images,
    model="mistral-large-latest",
    prompt="Extract all text from these images."
)

for i, result in enumerate(results):
    print(f"Image {i}: {result['text']}")
```

### Custom Prompts

```python
# Receipt-specific prompt
receipt_prompt = """
Please extract all text from this receipt image. Focus on:
1. Store name and address
2. Date and time
3. Item names and prices
4. Total amount
5. Tax information

Return the information in a structured format.
"""

result = await ocr.extract_text(
    image_bytes=receipt_bytes,
    prompt=receipt_prompt
)
```

## REST API Endpoints

### Extract Text from Single Image

```bash
POST /api/v2/ocr/extract-text
```

**Parameters:**
- `file` (required): Image file (JPEG, PNG, etc.)
- `provider` (optional): OCR provider (default: best available)
- `model` (optional): Specific model to use
- `prompt` (optional): Custom prompt for extraction

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v2/ocr/extract-text" \
  -F "file=@receipt.jpg" \
  -F "provider=mistral_vision" \
  -F "prompt=Extract all text from this receipt"
```

**Response:**
```json
{
  "text": "STORE NAME\n123 Main Street\nDate: 2024-01-15\nItems:\nMilk $3.99\nBread $2.50\nTotal: $6.49",
  "confidence": 0.95,
  "provider": "mistral_vision",
  "model_used": "mistral-large-latest",
  "tokens_used": 150,
  "cost": 0.001,
  "metadata": {
    "provider": "mistral_vision",
    "model": "mistral-large-latest",
    "image_size_bytes": 24576,
    "prompt_used": "Extract all text from this receipt"
  }
}
```

### Batch Text Extraction

```bash
POST /api/v2/ocr/extract-text-batch
```

**Parameters:**
- `files` (required): Multiple image files (max 10)
- `provider` (optional): OCR provider
- `model` (optional): Specific model
- `prompt` (optional): Custom prompt

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v2/ocr/extract-text-batch" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "provider=mistral_vision"
```

### Get Available Providers

```bash
GET /api/v2/ocr/providers
```

**Response:**
```json
{
  "providers": {
    "mistral_vision": {
      "available": true,
      "configured": true,
      "priority": 1
    },
    "azure_vision": {
      "available": true,
      "configured": false,
      "priority": 2
    }
  },
  "best_provider": "mistral_vision",
  "configured_count": 1
}
```

### Health Check

```bash
GET /api/v2/ocr/health
```

**Response:**
```json
{
  "status": "healthy",
  "providers": {
    "mistral_vision": {
      "status": "healthy",
      "models_count": 3,
      "available_models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"],
      "provider": "mistral_vision",
      "default_model": "mistral-large-latest"
    }
  }
}
```

## Best Practices

### 1. Image Quality

- **Resolution**: Use images with at least 300 DPI for best results
- **Format**: JPEG or PNG formats are recommended
- **Size**: Keep images under 10MB for optimal performance
- **Clarity**: Ensure good lighting and focus

### 2. Prompt Engineering

```python
# Good prompt for receipts
receipt_prompt = """
Extract all text from this receipt image. Please:
1. Maintain the original line structure
2. Include all numbers and prices
3. Preserve special characters
4. Identify store information clearly
5. Format dates consistently

Return the text exactly as it appears on the receipt.
"""

# Good prompt for documents
document_prompt = """
Analyze this document and extract all text content. Focus on:
1. Headers and titles
2. Body text
3. Tables and structured data
4. Footnotes and references
5. Page numbers if present

Maintain the document's logical structure in the output.
"""
```

### 3. Error Handling

```python
try:
    result = await ocr.extract_text(image_bytes)
    if result["text"]:
        # Process successful extraction
        process_text(result["text"])
    else:
        # Handle empty result
        logger.warning("No text extracted from image")
        
except Exception as e:
    logger.error(f"OCR processing failed: {e}")
    # Implement fallback strategy
    fallback_ocr_processing(image_bytes)
```

### 4. Cost Optimization

```python
# Use appropriate model based on task complexity
if is_simple_receipt(image_bytes):
    model = "mistral-small-latest"  # Lower cost
else:
    model = "mistral-large-latest"  # Higher accuracy

# Batch processing for multiple images
if len(images) > 1:
    results = await ocr.extract_text_batch(images)
else:
    result = await ocr.extract_text(images[0])
```

### 5. Performance Monitoring

```python
import time

start_time = time.time()
result = await ocr.extract_text(image_bytes)
processing_time = time.time() - start_time

logger.info(f"OCR completed in {processing_time:.2f}s, cost: ${result['cost']:.4f}")

# Monitor costs
if result['cost'] > 0.01:  # Alert for expensive operations
    logger.warning(f"High OCR cost: ${result['cost']:.4f}")
```

## Integration Examples

### Receipt Processing Service

```python
class ReceiptProcessor:
    def __init__(self):
        self.ocr = MistralVisionOCR(api_key=settings.MISTRAL_API_KEY)
    
    async def process_receipt(self, image_bytes: bytes) -> dict:
        """Process receipt image and extract structured data"""
        
        # Extract text
        ocr_result = await self.ocr.extract_text(
            image_bytes=image_bytes,
            prompt=self._get_receipt_prompt()
        )
        
        # Parse structured data
        parsed_data = self._parse_receipt_text(ocr_result["text"])
        
        return {
            "raw_text": ocr_result["text"],
            "parsed_data": parsed_data,
            "confidence": ocr_result["confidence"],
            "cost": ocr_result["cost"],
            "metadata": ocr_result["metadata"]
        }
    
    def _get_receipt_prompt(self) -> str:
        return """
        Extract all information from this receipt. Return in JSON format:
        {
            "store_name": "Store name",
            "date": "YYYY-MM-DD",
            "time": "HH:MM",
            "items": [
                {"name": "Item name", "price": 0.00, "quantity": 1}
            ],
            "subtotal": 0.00,
            "tax": 0.00,
            "total": 0.00
        }
        """
```

### Document Analysis Service

```python
class DocumentAnalyzer:
    def __init__(self):
        self.ocr = MistralVisionOCR(api_key=settings.MISTRAL_API_KEY)
    
    async def analyze_document(self, image_bytes: bytes) -> dict:
        """Analyze document content and structure"""
        
        # Extract text
        text_result = await self.ocr.extract_text(
            image_bytes=image_bytes,
            prompt="Extract all text from this document, maintaining structure."
        )
        
        # Analyze content
        analysis_result = await self.ocr.analyze_image(
            image_bytes=image_bytes,
            analysis_prompt="Analyze this document and identify: document type, key topics, important information, and structure."
        )
        
        return {
            "text": text_result["text"],
            "analysis": analysis_result["analysis"],
            "document_type": self._classify_document(text_result["text"]),
            "key_topics": self._extract_topics(text_result["text"]),
            "total_cost": text_result["cost"] + analysis_result["cost"]
        }
```

## Troubleshooting

### Common Issues

1. **API Key Invalid**
   ```
   Error: Mistral API key is required
   Solution: Verify API key in .env.online file
   ```

2. **Image Too Large**
   ```
   Error: Image size exceeds limit
   Solution: Resize image to under 10MB
   ```

3. **No Text Extracted**
   ```
   Warning: No text extracted from image
   Solution: Check image quality and try different prompt
   ```

4. **High Costs**
   ```
   Warning: High OCR cost detected
   Solution: Use smaller model for simple tasks
   ```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.getLogger("backend.core.ocr_providers.mistral_vision").setLevel(logging.DEBUG)
```

### Performance Tuning

1. **Model Selection**: Choose appropriate model based on task complexity
2. **Batch Processing**: Use batch endpoints for multiple images
3. **Caching**: Cache results for repeated images
4. **Async Processing**: Use async/await for non-blocking operations

## Cost Analysis

### Pricing (as of 2024)

| Model | Input Tokens | Output Tokens | Cost per 1K |
|-------|--------------|---------------|-------------|
| Large | $0.007 | $0.024 | $0.031 |
| Medium | $0.0024 | $0.0072 | $0.0096 |
| Small | $0.0007 | $0.0024 | $0.0031 |

### Cost Estimation

```python
def estimate_ocr_cost(image_count: int, model: str = "mistral-large-latest") -> float:
    """Estimate OCR processing cost"""
    
    # Average tokens per image (input + output)
    avg_tokens_per_image = 200  # Conservative estimate
    
    if model == "mistral-large-latest":
        cost_per_1k = 0.031
    elif model == "mistral-medium-latest":
        cost_per_1k = 0.0096
    else:  # small
        cost_per_1k = 0.0031
    
    total_tokens = image_count * avg_tokens_per_image
    estimated_cost = (total_tokens / 1000) * cost_per_1k
    
    return estimated_cost

# Example usage
cost = estimate_ocr_cost(100, "mistral-large-latest")
print(f"Estimated cost for 100 images: ${cost:.4f}")
```

## Security Considerations

1. **API Key Protection**: Store API keys securely, never commit to version control
2. **Input Validation**: Validate all image inputs before processing
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Data Privacy**: Ensure compliance with data protection regulations
5. **Error Handling**: Don't expose sensitive information in error messages

## Support

For issues and questions:

1. Check the [Mistral AI Documentation](https://docs.mistral.ai/)
2. Review application logs for detailed error information
3. Test with different images and prompts
4. Monitor costs and performance metrics
5. Contact support if issues persist 