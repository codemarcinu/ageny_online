# 🚀 Ageny Online

**Modern AI Assistant with External API Providers**

[![CI/CD](https://github.com/codemarcinu/ageny_online/workflows/CI/badge.svg)](https://github.com/codemarcinu/ageny_online/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](https://github.com/codemarcinu/ageny_online)

Ageny Online is a scalable, cloud-based AI assistant that leverages external API providers instead of local models, making it perfect for laptops without GPU requirements. It provides a cost-effective solution for AI-powered applications with enterprise-grade features.

## 📋 Overview

Ageny Online transforms local AI applications into cloud-ready solutions by eliminating GPU dependencies and leveraging external AI providers. This enables deployment on any laptop with internet access while maintaining high performance and reliability.

### 🎯 Key Benefits

- ✅ **No GPU Requirements** - runs on any laptop
- ✅ **Low Infrastructure Costs** - only API call costs
- ✅ **High Availability** - scalable cloud solution
- ✅ **Easy Deployment** - minimal configuration
- ✅ **Automatic Fallback** - provider redundancy
- ✅ **Enterprise Security** - API key encryption, rate limiting

## ✨ Features

- 🤖 **Multiple LLM Providers**: OpenAI GPT-4, Anthropic Claude, Cohere, Mistral AI
- 🔍 **Vector Search**: Pinecone, Weaviate integration
- 👁️ **OCR Capabilities**: Mistral Vision, Azure Vision, Google Vision
- 📊 **Monitoring**: Prometheus, Grafana dashboards
- 🔒 **Security**: Rate limiting, API key encryption, CORS
- 💰 **Cost Tracking**: Real-time usage monitoring and alerts
- 🐳 **Docker Ready**: Easy deployment with Docker Compose
- 🧪 **Testing**: Comprehensive test suite with >90% coverage
- 📚 **Documentation**: Detailed guides and API reference

## 🏗️ Architecture

### AI Components

| Component | Providers | Cost |
|-----------|-----------|------|
| **Chat Model** | OpenAI GPT-4, Mistral AI, Anthropic Claude | $0.01-0.03/1K tokens |
| **Embedding** | OpenAI, Mistral | $0.00002/1K tokens |
| **Vector Store** | Pinecone, Weaviate | $0.10/1K operations |
| **OCR** | Azure Vision, Google Vision, Mistral Vision | $1.50/1K transactions |

### Project Structure

```
ageny_online/
├── src/backend/
│   ├── core/
│   │   ├── llm_providers/     # OpenAI, Anthropic, Cohere, Mistral AI
│   │   ├── vector_stores/     # Pinecone, Weaviate
│   │   └── ocr_providers/     # Mistral Vision, Azure Vision, Google Vision
│   ├── agents/                # AI Agents
│   ├── api/                   # FastAPI endpoints
│   ├── models/                # Database models
│   ├── services/              # Business logic
│   └── schemas/               # Pydantic schemas
├── frontend/                  # React TypeScript frontend
├── config/                    # Configuration files
├── monitoring/                # Prometheus, Grafana configs
├── docs/                      # Documentation
└── tests/                     # Test suite
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
cp env.example .env.online
```

Edit `.env.online` and add your API keys:

```bash
# OpenAI (required)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Cohere (optional)
COHERE_API_KEY=your_cohere_api_key_here

# Mistral AI (optional)
MISTRAL_API_KEY=your_mistral_api_key_here

# Pinecone (optional)
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
- **Frontend**: http://localhost:3000
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
- [Roadmap](ROADMAP.md) - Project development plans and future features
- [Community Guidelines](COMMUNITY.md) - Community standards and guidelines
- [Release Notes](RELEASE_NOTES.md) - Version history and release information

## 🤝 Community

Join our growing community of AI enthusiasts and developers!

- **📖 [Community Guidelines](COMMUNITY.md)** - Learn about our values and standards
- **🗺️ [Roadmap](ROADMAP.md)** - See what's coming next
- **💬 [Discussions](https://github.com/codemarcinu/ageny_online/discussions)** - Join community conversations
- **🐛 [Issues](https://github.com/codemarcinu/ageny_online/issues)** - Report bugs and request features
- **📝 [Contributing](CONTRIBUTING.md)** - Learn how to contribute

### Community Stats
- 🌟 **Stars**: Help us reach 1000+ stars
- 🤝 **Contributors**: Join 50+ active contributors
- 📊 **Issues**: < 24h average response time
- 🚀 **Releases**: Regular updates and improvements

## 🗺️ Roadmap

Check out our [Roadmap](ROADMAP.md) to see what's coming next! We're actively working on:

- 🔥 **v1.1.0**: Enhanced conversation management and user authentication
- 🌟 **v1.2.0**: Enterprise features and multi-tenant architecture  
- 🚀 **v2.0.0**: Plugin system and advanced AI workflows

We welcome community input on our roadmap - feel free to [create an issue](https://github.com/codemarcinu/ageny_online/issues) with your suggestions!

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

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING_GUIDE.md) for details.

### Quick Start for Contributors

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/ageny_online.git
   cd ageny_online
   ```
3. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or venv\Scripts\activate  # Windows
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy environment file:
   ```bash
   cp env.example .env.online
   ```

### Development Workflow

1. Create feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. Make changes and write tests:
   ```bash
   # Edit code
   nano src/backend/core/my_feature.py
   
   # Write tests
   nano tests/unit/test_my_feature.py
   
   # Run tests
   pytest tests/unit/test_my_feature.py -v
   ```

3. Ensure all tests pass:
   ```bash
   pytest tests/unit/ --tb=short
   ```

4. Commit changes:
   ```bash
   git add .
   git commit -m 'feat: add amazing feature with tests'
   ```

5. Push to branch:
   ```bash
   git push origin feature/amazing-feature
   ```

6. Open Pull Request

### Code Style

- **Python**: PEP 8, black formatter
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for all classes and methods
- **Tests**: pytest, >90% coverage required

### Commit Messages

Use conventional commits:
- `feat:` - new feature
- `fix:` - bug fix
- `docs:` - documentation changes
- `test:`