# API Reference – Ageny Online

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints require API keys configured in the backend. No authentication header is required for public endpoints.

---

## Endpoints

### Health Check

- **GET** `/health`
- **Description:** Returns service health status.
- **Response:**
  ```json
  { "status": "ok" }
  ```

---

### Chat

- **POST** `/api/v1/chat`
- **Description:** Send a chat message to the AI assistant.
- **Request Body:**
  ```json
  {
    "message": "Hello world",
    "user_id": "user123"
  }
  ```
- **Response:**
  ```json
  {
    "response": "Hello! How can I help you?",
    "provider": "openai"
  }
  ```

---

### Providers Status

- **GET** `/api/v1/providers`
- **Description:** Returns availability of all configured providers.
- **Response:**
  ```json
  {
    "openai": true,
    "mistral": false,
    "azure_vision": true,
    "google_vision": false,
    "pinecone": true,
    "weaviate": false
  }
  ```

---

### OCR Text Extraction

- **POST** `/api/v2/ocr/extract-text`
- **Description:** Extract text from an image using selected OCR provider.
- **Request:**
  - `multipart/form-data` with fields:
    - `file`: image file
    - `provider`: (optional) provider name
- **Response:**
  ```json
  {
    "text": "Recognized text...",
    "provider": "mistral_vision"
  }
  ```

---

### Vector Store Search

- **POST** `/api/v2/vector-store/search`
- **Description:** Search documents in the vector store.
- **Request Body:**
  ```json
  {
    "query": "sample document",
    "index_name": "documents",
    "top_k": 5
  }
  ```
- **Response:**
  ```json
  {
    "results": [
      { "id": "doc1", "score": 0.98, "text": "..." }
    ]
  }
  ```

---

## Error Handling

All errors are returned as JSON with a `detail` field:

```json
{
  "detail": "Error message."
}
```

---

## More

- For full OpenAPI/Swagger docs, visit: `http://localhost:8000/docs`
- For more endpoints, see the backend source code and tests. 