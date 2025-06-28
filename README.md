# 🚀 Ageny Online

AI Assistant with external API providers (OpenAI, Anthropic, Cohere, Mistral AI, Pinecone, Azure Vision, Google Vision)

## 📋 Overview

Ageny Online is a modern AI assistant that leverages external API providers instead of local models, making it perfect for laptops without GPU requirements. It provides a scalable, cost-effective solution for AI-powered applications.

## ✨ Features

- 🤖 **Multiple LLM Providers**: OpenAI, Anthropic, Cohere, Mistral AI
- 🔍 **Vector Search**: Pinecone, Weaviate integration
- 👁️ **OCR Capabilities**: Mistral Vision, Azure Vision, Google Vision
- 📊 **Monitoring**: Prometheus, Grafana
- 🔒 **Security**: Rate limiting, API key encryption
- 💰 **Cost Tracking**: Real-time usage monitoring
- 🐳 **Docker Ready**: Easy deployment with Docker Compose
- 🧪 **Testing**: Comprehensive test suite with coverage
- 📚 **Documentation**: Detailed guides and API reference

## 🏗️ Architecture

```
ageny_online/
├── src/backend/
│   ├── core/
│   │   ├── llm_providers/     # OpenAI, Anthropic, Cohere, Mistral AI
│   │   ├── vector_stores/     # Pinecone, Weaviate
│   │   └── ocr_providers/     # Mistral Vision, Azure Vision, Google Vision
│   ├── agents/                # AI Agents
│   └── api/                   # FastAPI endpoints
├── config/                    # Configuration files
├── monitoring/                # Prometheus, Grafana configs
└── docs/                      # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- API Keys for desired providers

### 1. Clone Repository

```bash
git clone https://github.com/codemarcinu/ageny_online.git
cd ageny_online
```

### 2. Configure Environment

Copy the environment template and configure your API keys:

```bash
cp .env.online.example .env.online
```

Edit `.env.online` and add your API keys:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Cohere
COHERE_API_KEY=your_cohere_api_key_here

# Mistral AI
MISTRAL_API_KEY=your_mistral_api_key_here

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_environment_here

# Azure Vision (optional)
AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_VISION_KEY=your_azure_vision_key_here

# Google Vision (optional)
GOOGLE_VISION_CREDENTIALS_PATH=./config/google-credentials.json
GOOGLE_VISION_PROJECT_ID=your_google_vision_project_id_here
```

### 3. Run with Docker (Recommended)

```bash
# Start all services
docker-compose -f docker-compose.online.yaml up -d

# Check status
docker-compose -f docker-compose.online.yaml ps

# View logs
docker-compose -f docker-compose.online.yaml logs -f backend
```

### 4. Run Locally (Development)

```bash
# Install dependencies
poetry install

# Run the application
poetry run uvicorn src.backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Access Points

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

## 📡 API Usage

### Chat Endpoint

```bash
# GET request
curl "http://localhost:8000/api/v1/chat?message=Hello%20world"

# POST request
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello world", "user_id": "user123"}'
```

### Health Check

```bash
curl http://localhost:8000/health
```

### Providers Status

```bash
curl http://localhost:8000/api/v1/providers
```

### OCR Text Extraction

```bash
# Extract text from single image
curl -X POST "http://localhost:8000/api/v2/ocr/extract-text" \
  -F "file=@receipt.jpg" \
  -F "provider=mistral_vision"

# Extract text from multiple images
curl -X POST "http://localhost:8000/api/v2/ocr/extract-text-batch" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg"

# Get available OCR providers
curl http://localhost:8000/api/v2/ocr/providers

# Check OCR health
curl http://localhost:8000/api/v2/ocr/health
```

## 🔧 Configuration

### Provider Priority

Configure provider priorities in `.env.online`:

```bash
PROVIDER_PRIORITY_OPENAI=1
PROVIDER_PRIORITY_ANTHROPIC=2
PROVIDER_PRIORITY_COHERE=3
PROVIDER_PRIORITY_MISTRAL=4
```

### Rate Limiting

Configure in `.env.online`:

```bash
RATE_LIMIT_CHAT=100      # requests per minute
RATE_LIMIT_UPLOAD=10     # requests per minute
RATE_LIMIT_RAG=50        # requests per minute
```

### Cost Tracking

Configure in `.env.online`:

```bash
MONTHLY_BUDGET=100.0     # USD
COST_ALERT_THRESHOLD=80.0 # USD
```

## 📚 Documentation

- [Mistral OCR Guide](docs/MISTRAL_OCR_GUIDE.md) - Complete guide for Mistral AI Vision OCR
- [API Reference](docs/API_REFERENCE.md) - Detailed API documentation
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Production deployment instructions
- [Contributing Guide](docs/CONTRIBUTING_GUIDE.md) - Development guidelines

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test categories
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/e2e/

# Run OCR specific tests
poetry run pytest tests/unit/test_mistral_ocr.py
poetry run pytest tests/unit/test_ocr_factory.py
poetry run pytest tests/unit/test_ocr_endpoints.py
```

## 📊 Monitoring

### Metrics Available

- Request count by provider
- Response times
- Error rates
- Cost tracking
- Token usage
- OCR processing metrics
- Image processing performance

### Grafana Dashboards

1. **System Overview**: General health and performance
2. **Provider Metrics**: LLM provider performance
3. **OCR Analytics**: Image processing and text extraction metrics
4. **Cost Analysis**: Usage and cost tracking
5. **Error Tracking**: Error rates and types

## 🔒 Security

- API key encryption
- Rate limiting
- CORS configuration
- Input validation
- Error handling
- Image file validation
- OCR provider isolation

## 💰 Cost Optimization

### Provider Selection
- Configure provider priorities based on cost and performance needs
- Use smaller models for simple tasks
- Monitor usage with built-in cost tracking

### OCR Optimization
- Choose appropriate model size for image complexity
- Use batch processing for multiple images
- Implement caching for repeated images
- Monitor costs with real-time alerts

### Best Practices
- Set monthly budget limits
- Use rate limiting to prevent abuse
- Monitor provider performance and costs
- Implement fallback strategies

## 🚨 Troubleshooting

### Common Issues

1. **API Key Issues**
   ```bash
   # Check if API keys are configured
   curl http://localhost:8000/api/v1/providers
   ```

2. **OCR Processing Errors**
   ```bash
   # Check OCR provider health
   curl http://localhost:8000/api/v2/ocr/health
   ```

3. **High Costs**
   ```bash
   # Monitor costs in logs
   docker-compose -f docker-compose.online.yaml logs -f backend | grep "cost"
   ```

4. **Performance Issues**
   ```bash
   # Check system resources
   docker stats
   ```

### Debug Mode

Enable debug logging in `.env.online`:
```bash
LOG_LEVEL=DEBUG
DEBUG=true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/codemarcinu/ageny_online/issues)
- **Documentation**: [Wiki](https://github.com/codemarcinu/ageny_online/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/codemarcinu/ageny_online/discussions)

---

**Made with ❤️ by the Ageny Online Team** 