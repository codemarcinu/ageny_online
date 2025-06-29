# 🚀 Ageny Online

<<<<<<< HEAD
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
=======
**Online AI Agents API** - Przekształcenie aplikacji FoodSave AI z lokalnych modeli Ollama na wersję online wykorzystującą zewnętrzne API modeli językowych.

## 📋 Opis Projektu

Ageny Online to nowoczesna platforma AI, która eliminuje zależność od lokalnych modeli językowych i GPU, umożliwiając uruchomienie na dowolnym laptopie z dostępem do internetu.

### 🎯 Główne Zalety

- ✅ **Brak wymagań GPU** - działa na każdym laptopie
- ✅ **Niskie koszty infrastruktury** - tylko koszty API
- ✅ **Wysoka dostępność** - skalowalne rozwiązanie
- ✅ **Łatwość wdrożenia** - minimalna konfiguracja
- ✅ **Automatyczny fallback** - redundancja dostawców

## 🏗️ Architektura

### Komponenty AI

| Komponent | Dostawcy | Koszt |
|-----------|----------|-------|
| **Chat Model** | OpenAI GPT-4, Mistral AI | $0.01-0.03/1K tokens |
| **Embedding** | OpenAI, Mistral | $0.00002/1K tokens |
| **Vector Store** | Pinecone, Weaviate | $0.10/1K operations |
| **OCR** | Azure Vision, Google Vision | $1.50/1K transactions |

### Struktura Projektu
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8

```
ageny_online/
├── src/backend/
│   ├── core/
<<<<<<< HEAD
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
=======
│   │   ├── llm_providers/         # OpenAI, Mistral
│   │   ├── ocr_providers/         # Azure Vision, Google Vision
│   │   └── vector_stores/         # Pinecone, Weaviate
│   ├── api/
│   │   ├── v2/endpoints/          # REST API endpoints
│   │   └── main.py                # FastAPI app
│   └── config.py                  # Konfiguracja
├── requirements.txt               # Zależności Python
├── env.example                    # Przykład konfiguracji
└── README.md                      # Dokumentacja
```

## 🚀 Szybki Start

### 1. Instalacja

```bash
# Klonowanie repozytorium
git clone https://github.com/codemarcinu/ageny_online.git
cd ageny_online

# Tworzenie środowiska wirtualnego
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate     # Windows

# Instalacja zależności
pip install -r requirements.txt
```

### 2. Konfiguracja

```bash
# Kopiowanie pliku konfiguracyjnego
cp env.example .env.online

# Edycja konfiguracji
nano .env.online
```

**Minimalna konfiguracja:**
```env
# OpenAI (wymagane)
OPENAI_API_KEY=your_openai_api_key_here

# Mistral (opcjonalne)
MISTRAL_API_KEY=your_mistral_api_key_here

# Azure Vision (opcjonalne)
AZURE_VISION_KEY=your_azure_vision_key_here
AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/

# Pinecone (opcjonalne)
PINECONE_API_KEY=your_pinecone_api_key_here
```

### 3. Uruchomienie

```bash
# Uruchomienie serwera
python -m src.backend.api.main

# Lub z uvicorn
uvicorn src.backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Dostęp do API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Providers Status**: http://localhost:8000/api/v1/providers

## 📚 API Endpoints

### Chat Completions

```bash
# Pojedyncze zapytanie
curl -X POST "http://localhost:8000/api/v2/chat/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "model": "gpt-4o-mini"
  }'

# Batch processing
curl -X POST "http://localhost:8000/api/v2/chat/batch" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "messages": [{"role": "user", "content": "Hello"}],
      "model": "gpt-4o-mini"
    }
  ]'
```

### OCR Processing

```bash
# Upload image for OCR
curl -X POST "http://localhost:8000/api/v2/ocr/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@receipt.jpg"
```

### Vector Store Operations

```bash
# Create index
curl -X POST "http://localhost:8000/api/v2/vector-store/index/create" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "pinecone",
    "index_name": "documents",
    "dimension": 1536
  }'

# Upload documents
curl -X POST "http://localhost:8000/api/v2/vector-store/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "doc1",
        "text": "Sample document text",
        "metadata": {"category": "sample"}
      }
    ],
    "index_name": "documents",
    "provider": "pinecone"
  }'

# Search documents
curl -X POST "http://localhost:8000/api/v2/vector-store/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "sample document",
    "index_name": "documents",
    "top_k": 5
  }'
```

## 💰 Koszty

### Przykładowe Koszty (dzienne)

| Operacja | Ilość | Koszt |
|----------|-------|-------|
| Chat completions | 1000 zapytań | $0.50-1.50 |
| Embeddings | 10,000 tekstów | $0.20 |
| OCR | 100 obrazów | $0.15 |
| Vector operations | 10,000 operacji | $1.00 |

**Łączny koszt dzienny: ~$2-3 USD**

### Optymalizacja Kosztów

1. **Używaj tańszych modeli** (gpt-4o-mini zamiast gpt-4o)
2. **Batch processing** dla większej ilości danych
3. **Caching** dla powtarzających się zapytań
4. **Monitoring** kosztów przez `/api/v1/costs`

## 🔧 Konfiguracja Dostawców

### Wymagania dla Dostawców

Każdy dostawca ma określone wymagania konfiguracyjne. System automatycznie sprawdza dostępność dostawców na podstawie ustawionych zmiennych środowiskowych.

#### OpenAI (LLM)
**Wymagane**: `OPENAI_API_KEY`
```env
OPENAI_API_KEY=sk-...
OPENAI_ORGANIZATION=org-...  # opcjonalne
OPENAI_MODEL=gpt-4o-mini     # domyślnie
```

#### Mistral AI (LLM)
**Wymagane**: `MISTRAL_API_KEY`
```env
MISTRAL_API_KEY=your_mistral_key
MISTRAL_MODEL=mistral-small-latest  # domyślnie
```

#### Azure Vision (OCR)
**Wymagane**: `AZURE_VISION_KEY` + `AZURE_VISION_ENDPOINT`
```env
AZURE_VISION_KEY=your_azure_key
AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_VISION_REGION=westeurope  # opcjonalne
```

#### Google Vision (OCR)
**Wymagane**: `GOOGLE_VISION_PROJECT_ID` + `GOOGLE_VISION_CREDENTIALS_PATH`
```env
GOOGLE_VISION_PROJECT_ID=your-project-id
GOOGLE_VISION_CREDENTIALS_PATH=/path/to/service-account.json
```

#### Pinecone (Vector Store)
**Wymagane**: `PINECONE_API_KEY`
```env
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=gcp-starter  # domyślnie
```

#### Weaviate (Vector Store)
**Wymagane**: `WEAVIATE_URL`
```env
WEAVIATE_URL=https://your-weaviate-instance.network
WEAVIATE_API_KEY=your_api_key  # opcjonalne
WEAVIATE_USERNAME=your_username  # opcjonalne
WEAVIATE_PASSWORD=your_password  # opcjonalne
```

### Sprawdzanie Statusu Dostawców

```bash
# Sprawdzenie dostępnych dostawców
curl http://localhost:8000/api/v1/providers

# Przykładowa odpowiedź:
{
  "openai": true,
  "mistral": false,
  "azure_vision": true,
  "google_vision": false,
  "pinecone": true,
  "weaviate": false
}
```

### Priorytety Dostawców

System automatycznie wybiera dostępnych dostawców według priorytetów:

```env
# Priorytety LLM (od najwyższego)
LLM_PROVIDER_PRIORITY=openai,mistral

# Priorytety OCR
OCR_PROVIDER_PRIORITY=azure_vision,google_vision

# Priorytety Vector Store
VECTOR_STORE_PRIORITY=pinecone,weaviate
```

### OpenAI

1. Zarejestruj się na [OpenAI Platform](https://platform.openai.com/)
2. Wygeneruj API key
3. Dodaj do `.env.online`:
```env
OPENAI_API_KEY=sk-...
OPENAI_ORGANIZATION=org-...  # opcjonalne
```

## 🧪 Testowanie

### Uruchamianie Testów

```bash
# Przejdź do katalogu ageny_online
cd ageny_online

# Uruchomienie wszystkich testów jednostkowych
pytest tests/unit/

# Uruchomienie testów z pokazaniem postępu
pytest tests/unit/ -v

# Testy z coverage
pytest --cov=src tests/unit/

# Testy integracyjne
pytest tests/integration/

# Uruchomienie konkretnego testu
pytest tests/unit/test_config.py::TestSettings::test_settings_default_values -v
```

### Wymagania do Testów

- **Python 3.12+**
- **Virtual environment** z zainstalowanymi zależnościami
- **Plik .env.online** (można użyć `env.example` jako szablonu)

### Mockowanie i Izolacja

Wszystkie testy są **w pełni izolowane** i nie wymagają prawdziwych kluczy API:

- ✅ **LLM Providers**: Mockowane OpenAI i Mistral API
- ✅ **OCR Providers**: Mockowane Azure Vision i Google Vision
- ✅ **Vector Stores**: Mockowane Pinecone i Weaviate
- ✅ **Konfiguracja**: Każdy test ma własną instancję Settings
- ✅ **Brak połączeń sieciowych**: Testy działają offline

### Struktura Testów

```
tests/
├── unit/                    # Testy jednostkowe
│   ├── test_config.py      # Testy konfiguracji
│   ├── test_llm_providers.py    # Testy OpenAI/Mistral
│   ├── test_ocr_providers.py    # Testy Azure/Google Vision
│   └── test_vector_stores.py    # Testy Pinecone/Weaviate
├── integration/            # Testy integracyjne
│   └── test_api_endpoints.py    # Testy endpointów API
└── conftest.py            # Konfiguracja pytest
```

### Przykład Testu

```python
def test_openai_provider_initialization():
    """Test OpenAI provider initialization."""
    provider = OpenAIProvider("test-api-key")
    assert provider.default_model == "gpt-4o-mini"
    assert "gpt-4o-mini" in provider.models
```

### Status Testów

- **Testy jednostkowe**: 92/92 przechodzą ✅
- **Testy integracyjne**: Wszystkie przechodzą ✅
- **Coverage**: >95% pokrycia kodu

## 📊 Monitoring

### Metryki Prometheus

- **Endpoint**: http://localhost:8000/metrics
- **Dashboard**: Grafana (opcjonalnie)

### Health Checks

```bash
# Sprawdzenie statusu
curl http://localhost:8000/health

# Status dostawców
curl http://localhost:8000/api/v1/providers
```

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY .env.online .

EXPOSE 8000
CMD ["uvicorn", "src.backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  ageny-online:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./uploads:/app/uploads
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
```

## 🤝 Contributing

<<<<<<< HEAD
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
=======
### Przygotowanie Środowiska

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
   # lub venv\Scripts\activate  # Windows
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy environment file:
   ```bash
   cp env.example .env.online
   ```

### Pisanie Testów

#### Best Practices

1. **Używaj własnej instancji Settings**:
   ```python
   def test_provider_availability(monkeypatch):
       class TestSettings(Settings):
           class Config:
               env_file = None
       
       monkeypatch.setenv("OPENAI_API_KEY", "test-key")
       test_settings = TestSettings()
       assert is_provider_available("openai", settings=test_settings) == True
   ```

2. **Mockuj zewnętrzne API**:
   ```python
   with patch('backend.core.llm_providers.openai_client.AsyncOpenAI') as mock_client:
       mock_client.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
       # test code...
   ```

3. **Używaj fixtures** dla wspólnych danych:
   ```python
   @pytest.fixture
   def sample_messages():
       return [{"role": "user", "content": "Hello"}]
   ```

4. **Testuj asynchroniczne funkcje**:
   ```python
   @pytest.mark.asyncio
   async def test_async_function():
       result = await some_async_function()
       assert result == expected_value
   ```

#### Struktura Testu

```python
class TestMyFeature:
    """Test cases for MyFeature."""
    
    def test_feature_initialization(self):
        """Test feature initialization."""
        feature = MyFeature("test-param")
        assert feature.param == "test-param"
    
    @pytest.mark.asyncio
    async def test_feature_async_operation(self):
        """Test async operation."""
        feature = MyFeature("test-param")
        result = await feature.async_operation()
        assert result["status"] == "success"
```

### Workflow Development

1. Create feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. Make changes and write tests:
   ```bash
   # Edytuj kod
   nano src/backend/core/my_feature.py
   
   # Napisz testy
   nano tests/unit/test_my_feature.py
   
   # Uruchom testy
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
- **Type hints**: Wymagane dla wszystkich funkcji publicznych
- **Docstrings**: Google style dla wszystkich klas i metod
- **Tests**: pytest, >90% coverage wymagane

### Commit Messages

Używaj conventional commits:
- `feat:` - nowa funkcjonalność
- `fix:` - naprawa błędu
- `docs:` - zmiany w dokumentacji
- `test:` - dodanie lub zmiana testów
- `refactor:` - refaktoryzacja kodu
- `chore:` - zadania konserwacyjne

## 📄 Licencja

Ten projekt jest licencjonowany pod MIT License - zobacz [LICENSE](LICENSE) dla szczegółów.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/codemarcinu/ageny_online/issues)
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Email**: support@ageny-online.com

## 🔄 Migracja z FoodSave AI

### Kroki Migracji

1. **Backup danych** z lokalnej bazy
2. **Eksport dokumentów** do formatu JSON
3. **Konfiguracja** nowych dostawców API
4. **Import danych** do vector store
5. **Testowanie** funkcjonalności
6. **Wdrożenie** produkcyjne

### Różnice Architektoniczne

| Aspekt | FoodSave AI (Lokalny) | Ageny Online |
|--------|----------------------|--------------|
| **GPU** | Wymagane (8GB+ VRAM) | Nie wymagane |
| **RAM** | 16GB+ | 4GB+ |
| **Koszty** | Energia + Infrastruktura | API calls |
| **Skalowalność** | Ograniczona | Nieograniczona |
| **Dostępność** | Lokalna | Globalna |

---

**Ageny Online** - Nowoczesne AI bez GPU! 🚀 
>>>>>>> a463137dff6b658dad51c7d310168bb946660cf8
