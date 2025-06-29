## Testowanie jednostkowe frontend (React + Vitest)

Aby uruchomić testy jednostkowe dla komponentów React:

1. Zainstaluj zależności (jeśli nie są zainstalowane):
   ```bash
   npm install
   ```
2. Uruchom testy:
   ```bash
   npm run test
   ```
   Lub tryb watch (na żywo):
   ```bash
   npm run test:watch
   ```

Testy znajdują się w plikach `.test.tsx` w katalogach komponentów. Przykładowe testy dla ProductsSection i PointsDisplay pokazują, jak otaczać komponenty odpowiednimi providerami kontekstowymi.

Wskazówka: Jeśli komponent korzysta z contextu (np. ApiProvider, GamificationProvider), należy go otoczyć odpowiednim providerem w teście. 