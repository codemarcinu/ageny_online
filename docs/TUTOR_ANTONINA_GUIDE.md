# 🎓 Tutor Antonina - Przewodnik

## Wprowadzenie

**Tutor Antonina** to edukacyjny tryb w aplikacji Ageny Online, który pomaga użytkownikom tworzyć skuteczne prompty poprzez iteracyjne prowadzenie przez proces ulepszania.

## Jak to działa

### 1. Sześć kluczowych elementów skutecznego prompta

Tutor Antonina analizuje prompty pod kątem sześciu kluczowych elementów:

1. **Kontekst** - tło sytuacji, cel i okoliczności
2. **Instrukcja** - konkretne zadanie do wykonania
3. **Ograniczenia** - co NIE robić, ograniczenia techniczne
4. **Format odpowiedzi** - jak ma wyglądać odpowiedź
5. **Przykłady** - wzorce lub przykłady oczekiwanych rezultatów
6. **System prompt** - rola i styl komunikacji AI

### 2. Proces iteracyjny

1. **Wykrywanie brakujących elementów** - Tutor analizuje prompt i identyfikuje brakujące elementy
2. **Pytanie doprecyzowujące** - Zadaje jedno konkretne pytanie o brakujący element
3. **Korekta** - Użytkownik odpowiada na pytanie, uzupełniając prompt
4. **Sugestia** - Gdy wszystkie elementy są obecne, Tutor podaje sugestię ulepszenia i zoptymalizowaną wersję

## Jak używać

### Włączanie trybu Tutor Antoniny

1. Przejdź do strony **Chat z AI**
2. Włącz checkbox **"Tutor Antonina"** w prawym górnym rogu
3. Napisz swój prompt i wyślij wiadomość

### Przykład użycia

**Użytkownik:** "Napisz esej"

**Tutor Antonina:** "W jakim kontekście chcesz użyć tego prompta? Czy to zadanie szkolne, praca, czy coś innego?"

**Użytkownik:** "To zadanie szkolne z historii o II wojnie światowej"

**Tutor Antonina:** "Sugestia: Twój prompt jest lepszy, ale dodaj konkretny format odpowiedzi.

Ulepszony prompt: 
Jesteś doświadczonym nauczycielem historii. Napisz esej o II wojnie światowej dla ucznia szkoły średniej. Esej powinien mieć:
- Wstęp (2-3 zdania)
- 3 główne punkty z przykładami
- Podsumowanie (2-3 zdania)
- Maksymalnie 500 słów
- Język dostosowany do poziomu szkoły średniej"

## API Endpoints

### 1. Chat z trybem Tutor

```http
POST /api/v2/chat/chat
```

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Napisz esej"}
  ],
  "tutor_mode": true
}
```

**Response:**
```json
{
  "text": "Odpowiedź AI...",
  "tutor_question": "W jakim kontekście chcesz użyć tego prompta?",
  "tutor_feedback": null,
  "model": "gpt-4",
  "provider": "openai",
  "usage": {...},
  "cost": 0.001,
  "finish_reason": "stop",
  "response_time": 1.23
}
```

### 2. Dedykowany endpoint Tutor

```http
POST /api/v2/chat/tutor
```

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Napisz esej"}
  ],
  "model": "gpt-4",
  "provider": "openai"
}
```

**Response:**
```json
{
  "reply": "Odpowiedź AI...",
  "tutor_question": "W jakim kontekście chcesz użyć tego prompta?",
  "tutor_feedback": null,
  "model": "gpt-4",
  "provider": "openai",
  "usage": {...},
  "cost": 0.001,
  "finish_reason": "stop",
  "response_time": 1.23
}
```

## Gamifikacja

Tryb Tutor Antoniny oferuje dodatkowe możliwości gamifikacji:

- **Bonusowe punkty**: +15 punktów za każdą wiadomość w trybie tutor
- **Osiągnięcie "Mistrz Promptów"**: Odblokowane po otrzymaniu pierwszej sugestii
- **Wyzwanie dzienne**: "Użyj trybu Tutor 5 razy dziennie"

## Techniczne szczegóły

### Backend

- **Agent**: `TutorAntonina` w `src/backend/agents/tutor_agent.py`
- **Schematy**: `TutorRequest` i `TutorResponse` w `src/backend/schemas/tutor.py`
- **Endpointy**: Rozszerzone w `src/backend/api/v2/endpoints/chat.py`

### Frontend

- **Komponent**: `TutorHints` w `frontend/src/components/TutorHints.tsx`
- **Integracja**: Rozszerzony `ChatPage` o obsługę trybu tutor
- **Styling**: Wykorzystuje istniejące klasy Tailwind CSS

### Testy

- **Testy jednostkowe**: `tests/unit/test_tutor_agent.py`
- **Testy integracyjne**: `tests/integration/test_tutor_endpoints.py`
- **Testy frontendu**: `frontend/src/components/TutorHints.test.tsx`

## Najlepsze praktyki

### Dla użytkowników

1. **Bądź konkretny** - Im bardziej szczegółowy prompt, tym lepsza sugestia
2. **Odpowiadaj na pytania** - Pytania tutora prowadzą do lepszego prompta
3. **Używaj iteracyjnie** - Każda odpowiedź na pytanie poprawia prompt
4. **Ucz się z sugestii** - Analizuj zoptymalizowane wersje, aby lepiej rozumieć strukturę

### Dla deweloperów

1. **Obsługa błędów** - Tryb tutor nie powinien przerywać głównej funkcjonalności czatu
2. **Optymalizacja** - Używaj niskiej temperatury (0.2) dla spójności odpowiedzi
3. **Logowanie** - Monitoruj użycie trybu tutor dla analizy
4. **Testy** - Sprawdzaj różne scenariusze promptów

## Rozwiązywanie problemów

### Częste problemy

1. **Tutor nie zadaje pytań** - Sprawdź czy tryb jest włączony w interfejsie
2. **Brak sugestii** - Upewnij się, że prompt zawiera wszystkie 6 elementów
3. **Błędy API** - Sprawdź logi backendu pod kątem błędów LLM providera

### Debugowanie

```bash
# Sprawdź logi backendu
tail -f logs/backend.log | grep "Tutor"

# Uruchom testy
pytest tests/unit/test_tutor_agent.py -v
pytest tests/integration/test_tutor_endpoints.py -v
```

## Przyszłe rozszerzenia

- **Historia promptów** - Zapisywanie i analiza postępów użytkownika
- **Personalizacja** - Dostosowanie do poziomu zaawansowania użytkownika
- **Więcej przykładów** - Biblioteka wzorcowych promptów
- **Analiza statystyk** - Raporty skuteczności promptów 