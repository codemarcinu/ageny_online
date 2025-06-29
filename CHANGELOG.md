# Changelog

Wszystkie istotne zmiany w projekcie Ageny Online będą dokumentowane w tym pliku.

Format jest oparty na [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
a projekt przestrzega [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Kompletny system testów jednostkowych i integracyjnych
- Mockowanie wszystkich zewnętrznych API (OpenAI, Mistral, Azure Vision, Google Vision, Pinecone, Weaviate)
- Izolacja środowiska testowego z własnymi instancjami Settings
- Automatyczne sprawdzanie dostępności dostawców
- System priorytetów dostawców z automatycznym fallbackiem
- Walidacja konfiguracji dostawców
- Obsługa asynchronicznych operacji w testach

### Changed
- Refaktoryzacja systemu konfiguracji (Pydantic v2, Enumy, dataclasses)
- Aktualizacja klientów Pinecone i Weaviate do najnowszych API
- Zmiana importów z absolutnych na względne
- Poprawa struktury testów i organizacji kodu

### Fixed
- Błędy importów w endpointach API
- Problemy z mockowaniem asynchronicznych funkcji
- Błędy walidacji konfiguracji dostawców
- Problemy z cache'owaniem ustawień w testach
- Błędy w testach Google Vision (TextDetectionParams)
- Problemy z testami Weaviate (mockowanie klienta)

### Technical
- **Test Coverage**: >95% pokrycia kodu
- **Test Status**: 92/92 testów jednostkowych przechodzi
- **Python Version**: 3.12+
- **Dependencies**: Zaktualizowane do najnowszych wersji

## [0.1.0] - 2024-01-XX

### Added
- Podstawowa architektura Ageny Online
- Integracja z OpenAI GPT-4
- Integracja z Mistral AI
- Integracja z Azure Vision OCR
- Integracja z Google Vision OCR
- Integracja z Pinecone Vector Store
- Integracja z Weaviate Vector Store
- FastAPI backend z endpointami REST
- System konfiguracji z obsługą zmiennych środowiskowych
- Podstawowa dokumentacja API

### Technical
- **Framework**: FastAPI
- **Python**: 3.11+
- **Database**: Vector stores (Pinecone, Weaviate)
- **AI Models**: OpenAI GPT-4, Mistral AI
- **OCR**: Azure Vision, Google Vision

---

## Jak czytać ten changelog

- **Added** - nowe funkcjonalności
- **Changed** - zmiany w istniejących funkcjonalnościach
- **Deprecated** - funkcjonalności oznaczone jako przestarzałe
- **Removed** - usunięte funkcjonalności
- **Fixed** - naprawione błędy
- **Security** - poprawki bezpieczeństwa
- **Technical** - zmiany techniczne i infrastrukturalne 