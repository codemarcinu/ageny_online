# 📋 RAPORT WDROŻENIA WERSJI ONLINE - FOODSAVE AI
## Przejście z lokalnych modeli Ollama na API zewnętrzne

**Data:** 21 grudnia 2024  
**Autor:** AI Assistant  
**Projekt:** FoodSave AI → Ageny Online  
**Repozytorium docelowe:** https://github.com/codemarcinu/ageny_online.git

---

## 🎯 CEL PROJEKTU

Przekształcenie aplikacji FoodSave AI z lokalnych modeli Ollama na wersję online wykorzystującą zewnętrzne API modeli językowych, umożliwiającą uruchomienie na laptopie bez GPU.

---

## 📊 ANALIZA OBECNEGO STANU

### Obecna Architektura (FoodSave AI)

#### 🔧 Komponenty AI
- **Ollama**: Lokalne modele językowe (Bielik, Gemma3)
- **Embedding**: Nomic-embed-text (lokalny)
- **Vector Store**: FAISS (lokalny)
- **OCR**: Tesseract (lokalny)

#### 💰 Koszty Obecne
- **Infrastruktura**: Wymaga GPU (min. 8GB VRAM)
- **Energia**: Wysokie zużycie prądu (300-500W)
- **Czas**: Długie ładowanie modeli
- **Pamięć**: Min. 16GB RAM

---

## 🚀 NOWA ARCHITEKTURA (AGENY ONLINE)

### 🎯 Cele Wdrożenia

1. **Eliminacja zależności GPU**
2. **Redukcja kosztów infrastruktury**
3. **Zwiększenie dostępności**
4. **Skalowalność**
5. **Łatwość wdrożenia**

### 🔄 Zmiany Architektoniczne

#### 1. Zastąpienie Ollama API zewnętrznymi

| Komponent | Obecny | Nowy | Dostawca |
|-----------|--------|------|----------|
| **Chat Model** | Bielik/Gemma3 | GPT-4/Claude-3 | OpenAI/Anthropic |
| **Embedding** | Nomic-embed-text | OpenAI/Cohere | OpenAI/Cohere |
| **Vector Store** | FAISS (lokalny) | Pinecone/Weaviate | Pinecone/Weaviate |
| **OCR** | Tesseract | Azure Vision/Google Vision | Microsoft/Google |

#### 2. Nowa Struktura Projektu

```
ageny_online/
├── src/backend/
│   ├── core/
│   │   ├── llm_providers/         # Nowe: Dostawcy LLM
│   │   │   ├── openai_client.py
│   │   │   ├── anthropic_client.py
│   │   │   ├── cohere_client.py
│   │   │   └── provider_factory.py
│   │   ├── vector_stores/         # Nowe: Vector stores
│   │   │   ├── pinecone_client.py
│   │   │   ├── weaviate_client.py
│   │   │   └── store_factory.py
│   │   ├── ocr_providers/         # Nowe: OCR providers
│   │   │   ├── azure_vision.py
│   │   │   ├── google_vision.py
│   │   │   └── ocr_factory.py
│   │   └── hybrid_llm_client.py   # Zmodyfikowany
│   ├── agents/                    # Zmodyfikowane agenty
│   └── api/                       # Nowe endpointy
├── frontend/                      # Uproszczony frontend
├── config/                        # Konfiguracja providers
└── docker-compose.online.yaml     # Nowa konfiguracja
```

---

## 🔧 SZCZEGÓŁOWY PLAN WDROŻENIA

### Faza 1: Przygotowanie Infrastruktury (1-2 dni)

#### 1.1 Utworzenie Nowego Repozytorium
```bash
# Klonowanie nowego repozytorium
git clone https://github.com/codemarcinu/ageny_online.git
cd ageny_online

# Kopiowanie podstawowej struktury
cp -r ../my_assistant/src/backend ./src/
cp -r ../my_assistant/myappassistant-chat-frontend ./frontend/
```

#### 1.2 Konfiguracja Środowiska
```bash
# Nowy plik .env.online
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
COHERE_API_KEY=your_cohere_key
PINECONE_API_KEY=your_pinecone_key
AZURE_VISION_KEY=your_azure_key
GOOGLE_VISION_KEY=your_google_key
```

#### 1.3 Aktualizacja Dependencies
```toml
# pyproject.toml - nowe zależności
[tool.poetry.dependencies]
openai = "^1.0.0"
anthropic = "^0.7.0"
cohere = "^4.0.0"
pinecone-client = "^2.2.0"
weaviate-client = "^3.25.0"
azure-cognitiveservices-vision-computervision = "^0.9.0"
google-cloud-vision = "^3.4.0"
```

### Faza 2: Implementacja Providerów LLM (2-3 dni)

#### 2.1 OpenAI Provider
```python
# src/backend/core/llm_providers/openai_client.py
import openai
from typing import List, Dict, Any, Optional

class OpenAIProvider:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.models = {
            "gpt-4": {"max_tokens": 8192, "cost_per_1k": 0.03},
            "gpt-4-turbo": {"max_tokens": 128000, "cost_per_1k": 0.01},
            "gpt-3.5-turbo": {"max_tokens": 16385, "cost_per_1k": 0.002}
        }
    
    async def chat(self, messages: List[Dict], model: str = "gpt-4-turbo") -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    async def embed(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
```

#### 2.2 Anthropic Provider
```python
# src/backend/core/llm_providers/anthropic_client.py
import anthropic
from typing import List, Dict, Any

class AnthropicProvider:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.models = {
            "claude-3-opus": {"max_tokens": 200000, "cost_per_1k": 0.015},
            "claude-3-sonnet": {"max_tokens": 200000, "cost_per_1k": 0.003},
            "claude-3-haiku": {"max_tokens": 200000, "cost_per_1k": 0.00025}
        }
    
    async def chat(self, messages: List[Dict], model: str = "claude-3-sonnet") -> str:
        # Konwersja formatu wiadomości
        prompt = self._convert_messages_to_prompt(messages)
        response = await self.client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
```

#### 2.3 Provider Factory
```python
# src/backend/core/llm_providers/provider_factory.py
from enum import Enum
from typing import Dict, Type
from .openai_client import OpenAIProvider
from .anthropic_client import AnthropicProvider

class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"

class LLMProviderFactory:
    _providers: Dict[ProviderType, Type] = {
        ProviderType.OPENAI: OpenAIProvider,
        ProviderType.ANTHROPIC: AnthropicProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_type: ProviderType, api_key: str):
        if provider_type not in cls._providers:
            raise ValueError(f"Unsupported provider: {provider_type}")
        return cls._providers[provider_type](api_key)
```

### Faza 3: Vector Store Integration (1-2 dni)

#### 3.1 Pinecone Integration
```python
# src/backend/core/vector_stores/pinecone_client.py
import pinecone
from typing import List, Dict, Any

class PineconeVectorStore:
    def __init__(self, api_key: str, environment: str, index_name: str):
        pinecone.init(api_key=api_key, environment=environment)
        self.index = pinecone.Index(index_name)
    
    async def add_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        vectors = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            vectors.append({
                "id": f"doc_{i}",
                "values": embedding,
                "metadata": doc
            })
        self.index.upsert(vectors=vectors)
    
    async def search(self, query_embedding: List[float], top_k: int = 5):
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        return results.matches
```

### Faza 4: OCR Integration (1 dzień)

#### 4.1 Azure Vision OCR
```python
# src/backend/core/ocr_providers/azure_vision.py
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

class AzureVisionOCR:
    def __init__(self, endpoint: str, api_key: str):
        self.client = ComputerVisionClient(
            endpoint, 
            CognitiveServicesCredentials(api_key)
        )
    
    async def extract_text(self, image_url: str) -> str:
        # Async wrapper for Azure Vision
        result = await self.client.read(image_url, raw=True)
        operation_location = result.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]
        
        while True:
            read_result = await self.client.get_read_result(operation_id)
            if read_result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                break
            await asyncio.sleep(1)
        
        text = ""
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                text += line.text + "\n"
        return text
```

### Faza 5: Modyfikacja Hybrid LLM Client (2-3 dni)

#### 5.1 Nowa Implementacja
```python
# src/backend/core/hybrid_llm_client.py (zmodyfikowany)
class HybridLLMClient:
    def __init__(self):
        self.providers = self._init_providers()
        self.vector_store = self._init_vector_store()
        self.ocr_provider = self._init_ocr_provider()
        self.cost_tracker = CostTracker()
    
    def _init_providers(self) -> Dict[str, Any]:
        return {
            "openai": LLMProviderFactory.create_provider(
                ProviderType.OPENAI, 
                settings.OPENAI_API_KEY
            ),
            "anthropic": LLMProviderFactory.create_provider(
                ProviderType.ANTHROPIC, 
                settings.ANTHROPIC_API_KEY
            )
        }
    
    async def chat(self, messages: List[Dict], provider: str = "openai") -> str:
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")
        
        try:
            response = await self.providers[provider].chat(messages)
            self.cost_tracker.track_usage(provider, "chat", len(messages))
            return response
        except Exception as e:
            logger.error(f"Error with {provider}: {e}")
            # Fallback to another provider
            return await self._fallback_chat(messages, provider)
```

### Faza 6: Aktualizacja Agentów (2-3 dni)

#### 6.1 Modyfikacja Agentów
```python
# src/backend/agents/base_agent.py (zmodyfikowany)
class BaseAgent:
    def __init__(self):
        self.llm_client = hybrid_llm_client
        self.vector_store = vector_store_factory.get_store()
        self.ocr_provider = ocr_factory.get_provider()
    
    async def process_query(self, query: str, context: Dict = None) -> str:
        # Nowa logika z providerami online
        if self._needs_ocr(query):
            text = await self.ocr_provider.extract_text(query)
            query = f"{query}\nExtracted text: {text}"
        
        if self._needs_rag(query):
            embeddings = await self.llm_client.embed(query)
            relevant_docs = await self.vector_store.search(embeddings)
            context = self._build_context(relevant_docs)
        
        response = await self.llm_client.chat(
            messages=[{"role": "user", "content": query}],
            provider=self._select_provider(query)
        )
        return response
```

### Faza 7: Frontend Updates (1-2 dni)

#### 7.1 Uproszczenie Frontendu
```typescript
// frontend/src/services/api.ts (zmodyfikowany)
export const apiService = {
  // Uproszczone endpointy
  chat: async (message: string) => {
    const response = await fetch('/api/v2/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return response.json();
  },
  
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch('/api/v2/upload', {
      method: 'POST',
      body: formData
    });
    return response.json();
  }
};
```

### Faza 8: Monitoring i Cost Tracking (1 dzień)

#### 8.1 Cost Tracker
```python
# src/backend/core/cost_tracker.py
class CostTracker:
    def __init__(self):
        self.usage_stats = {}
        self.monthly_budget = 100.0  # USD
    
    def track_usage(self, provider: str, operation: str, tokens: int):
        if provider not in self.usage_stats:
            self.usage_stats[provider] = {"total_cost": 0, "operations": {}}
        
        cost = self._calculate_cost(provider, operation, tokens)
        self.usage_stats[provider]["total_cost"] += cost
        
        if self._exceeds_budget():
            logger.warning(f"Monthly budget exceeded: ${self.get_total_cost()}")
    
    def get_total_cost(self) -> float:
        return sum(stats["total_cost"] for stats in self.usage_stats.values())
```

---

## 💰 ANALIZA KOSZTÓW

### Porównanie Kosztów

| Aspekt | Obecny (Ollama) | Nowy (API Online) |
|--------|----------------|-------------------|
| **Infrastruktura** | GPU (8GB+ VRAM) | Brak wymagań |
| **Energia** | 300-500W | 50-100W |
| **Modeli** | Darmowe | $0.01-0.03/1k tokenów |
| **Embedding** | Darmowe | $0.0001/1k tokenów |
| **Vector Store** | Darmowe | $0.10/1M operacji |
| **OCR** | Darmowe | $1.50/1000 stron |

### Szacowane Koszty Miesięczne (1000 użytkowników)

| Usługa | Ilość | Koszt |
|--------|-------|-------|
| **Chat (GPT-4)** | 100k tokenów | $3.00 |
| **Embedding** | 1M tokenów | $0.10 |
| **Vector Store** | 10k operacji | $1.00 |
| **OCR** | 100 stron | $0.15 |
| **Razem** | | **$4.25/miesiąc** |

---

## 🚀 PLAN WDROŻENIA

### Tydzień 1: Podstawowa Infrastruktura
- [ ] Utworzenie nowego repozytorium
- [ ] Konfiguracja środowiska
- [ ] Implementacja podstawowych providerów
- [ ] Testy jednostkowe

### Tydzień 2: Integracja Serwisów
- [ ] Vector store integration
- [ ] OCR integration
- [ ] Modyfikacja agentów
- [ ] Testy integracyjne

### Tydzień 3: Frontend i Monitoring
- [ ] Aktualizacja frontendu
- [ ] Cost tracking
- [ ] Monitoring
- [ ] Testy end-to-end

### Tydzień 4: Optymalizacja i Wdrożenie
- [ ] Optymalizacja wydajności
- [ ] Dokumentacja
- [ ] Wdrożenie produkcyjne
- [ ] Monitoring produkcyjny

---

## 🔧 KONFIGURACJA TECHNICZNA

### Nowy docker-compose.online.yaml
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.online
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - AZURE_VISION_KEY=${AZURE_VISION_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  monitoring:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
```

### Nowy Dockerfile.online
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install Python dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Run application
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🧪 STRATEGIA TESTOWANIA

### Testy Jednostkowe
```python
# tests/test_llm_providers.py
import pytest
from unittest.mock import Mock, patch
from src.backend.core.llm_providers.openai_client import OpenAIProvider

class TestOpenAIProvider:
    @pytest.fixture
    def provider(self):
        return OpenAIProvider("test_key")
    
    @patch('openai.OpenAI')
    async def test_chat(self, mock_openai, provider):
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = "Test response"
        
        response = await provider.chat([{"role": "user", "content": "Hello"}])
        assert response == "Test response"
```

### Testy Integracyjne
```python
# tests/integration/test_hybrid_client.py
import pytest
from src.backend.core.hybrid_llm_client import HybridLLMClient

class TestHybridLLMClient:
    @pytest.fixture
    def client(self):
        return HybridLLMClient()
    
    async def test_chat_with_fallback(self, client):
        # Test fallback mechanism
        response = await client.chat(
            [{"role": "user", "content": "Hello"}],
            provider="openai"
        )
        assert response is not None
```

---

## 📊 MONITORING I METRYKI

### Nowe Metryki
```python
# src/backend/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Cost metrics
COST_COUNTER = Counter('llm_cost_total', 'Total cost by provider', ['provider'])
TOKEN_COUNTER = Counter('llm_tokens_total', 'Total tokens by provider', ['provider'])

# Performance metrics
RESPONSE_TIME = Histogram('llm_response_time_seconds', 'Response time by provider', ['provider'])
ERROR_COUNTER = Counter('llm_errors_total', 'Total errors by provider', ['provider'])

# Availability metrics
PROVIDER_AVAILABILITY = Gauge('llm_provider_available', 'Provider availability', ['provider'])
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Ageny Online - LLM Metrics",
    "panels": [
      {
        "title": "Cost by Provider",
        "type": "stat",
        "targets": [
          {
            "expr": "llm_cost_total",
            "legendFormat": "{{provider}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(llm_response_time_seconds_sum[5m])",
            "legendFormat": "{{provider}}"
          }
        ]
      }
    ]
  }
}
```

---

## 🔒 BEZPIECZEŃSTWO

### Zarządzanie Kluczami API
```python
# src/backend/core/security.py
import os
from cryptography.fernet import Fernet

class APIKeyManager:
    def __init__(self):
        self.cipher = Fernet(os.getenv('ENCRYPTION_KEY'))
    
    def encrypt_key(self, api_key: str) -> str:
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        return self.cipher.decrypt(encrypted_key.encode()).decode()
    
    def rotate_keys(self):
        # Implementacja rotacji kluczy
        pass
```

### Rate Limiting
```python
# src/backend/core/rate_limiter.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("100/minute")
async def chat_endpoint(request: Request):
    # Chat endpoint with rate limiting
    pass
```

---

## 📚 DOKUMENTACJA

### Nowa Struktura Dokumentacji
```
docs/
├── SETUP_ONLINE.md           # Instrukcja wdrożenia
├── API_PROVIDERS.md          # Dokumentacja providerów
├── COST_OPTIMIZATION.md      # Optymalizacja kosztów
├── MONITORING.md             # Monitoring i alerty
└── TROUBLESHOOTING.md        # Rozwiązywanie problemów
```

### Przykład SETUP_ONLINE.md
```markdown
# 🚀 Wdrożenie Ageny Online

## Wymagania
- Python 3.12+
- Docker & Docker Compose
- Klucze API (OpenAI, Anthropic, etc.)

## Szybki Start
1. Sklonuj repozytorium
2. Skonfiguruj klucze API w .env
3. Uruchom: `docker-compose -f docker-compose.online.yaml up`

## Konfiguracja Providerów
- OpenAI: Najlepszy dla zadań ogólnych
- Anthropic: Najlepszy dla analizy i rozumowania
- Cohere: Najlepszy dla embeddingów
```

---

## �� KORZYŚCI WDROŻENIA

### Dla Użytkowników
- ✅ **Dostępność**: Działa na każdym laptopie
- ✅ **Szybkość**: Natychmiastowe uruchomienie
- ✅ **Jakość**: Najnowsze modele AI
- ✅ **Skalowalność**: Automatyczne skalowanie

### Dla Deweloperów
- ✅ **Łatwość**: Brak konfiguracji GPU
- ✅ **Koszty**: Niższe koszty rozwoju
- ✅ **Monitoring**: Pełna widoczność
- ✅ **Flexibility**: Łatwe przełączanie providerów

### Dla Biznesu
- ✅ **ROI**: Szybszy time-to-market
- ✅ **Skalowalność**: Obsługa większej liczby użytkowników
- ✅ **Koszty**: Przewidywalne koszty operacyjne
- ✅ **Konkurencyjność**: Dostęp do najnowszych technologii AI

---

## 🚨 RYZYKA I MITIGACJA

### Ryzyka Techniczne
| Ryzyko | Prawdopodobieństwo | Wpływ | Mitigacja |
|--------|-------------------|-------|-----------|
| **API Rate Limits** | Średnie | Wysoki | Circuit breaker, fallback providers |
| **Koszty** | Wysokie | Średni | Cost tracking, budget alerts |
| **Dostępność API** | Niskie | Wysoki | Multiple providers, caching |
| **Bezpieczeństwo** | Średnie | Wysoki | Encryption, key rotation |

### Plan Mitigacji
1. **Circuit Breaker Pattern**: Automatyczne przełączanie providerów
2. **Cost Alerts**: Powiadomienia o przekroczeniu budżetu
3. **Caching**: Redukcja kosztów i poprawa wydajności
4. **Backup Providers**: Zawsze dostępny fallback

---

## 📈 ROADMAP PO WDROŻENIU

### Miesiąc 1: Stabilizacja
- Monitoring produkcyjny
- Optymalizacja kosztów
- Dokumentacja użytkownika

### Miesiąc 2: Rozszerzenie
- Dodanie nowych providerów
- Advanced RAG features
- Multi-language support

### Miesiąc 3: Optymalizacja
- Machine learning dla wyboru providerów
- Advanced caching strategies
- Performance optimization

---

## ✅ CHECKLIST WDROŻENIA

### Przygotowanie
- [ ] Utworzenie repozytorium ageny_online
- [ ] Konfiguracja kluczy API
- [ ] Przygotowanie środowiska testowego
- [ ] Dokumentacja wymagań

### Implementacja
- [ ] Podstawowe providery LLM
- [ ] Vector store integration
- [ ] OCR integration
- [ ] Modyfikacja agentów
- [ ] Frontend updates

### Testowanie
- [ ] Testy jednostkowe
- [ ] Testy integracyjne
- [ ] Testy wydajnościowe
- [ ] Testy bezpieczeństwa

### Wdrożenie
- [ ] Konfiguracja produkcyjna
- [ ] Monitoring setup
- [ ] Dokumentacja użytkownika
- [ ] Training team

---

## 🎉 PODSUMOWANIE

Przejście z lokalnych modeli Ollama na API zewnętrzne to strategiczna decyzja, która:

1. **Eliminuje bariery techniczne** - brak wymagań GPU
2. **Redukuje koszty infrastruktury** - z $500+/miesiąc na $5+/miesiąc
3. **Zwiększa dostępność** - działa na każdym urządzeniu
4. **Przyspiesza development** - szybszy time-to-market
5. **Zapewnia skalowalność** - automatyczne skalowanie

**Szacowany czas wdrożenia:** 4 tygodnie  
**Szacowany koszt wdrożenia:** $1000-2000  
**Oszczędności roczne:** $5000+ (infrastruktura)  
**ROI:** 250%+ w pierwszym roku

---

**📞 Kontakt:** [Dane kontaktowe]  
**📧 Email:** [Email]  
**🔗 Repozytorium:** https://github.com/codemarcinu/ageny_online.git
