# 🍳 PLAN ROZSZERZENIA O FUNKCJONALNOŚCI KULINARNE - ANTONINA

## 📋 PRZEGLĄD PROJEKTU

**Data:** 2024-10-29  
**Cel:** Rozszerzenie Ageny Online o funkcjonalności kulinarne dla Antoniny  
**Status:** Planowanie → Dokumentacja → Implementacja

## 🎯 CEL PROJEKTU

Antonina lubi gotować i chce mieć możliwość:
1. **Wprowadzania danych produktów spożywczych** (ręcznie lub przez skan)
2. **Planowania zakupów** z pomocą AI
3. **Generowania przepisów** na podstawie dostępnych składników
4. **Kontroli budżetu** na jedzenie
5. **Śledzenia wartości odżywczych**

## 🏗️ ARCHITEKTURA ROZSZERZENIA

### 📊 NOWE MODELE BAZY DANYCH

#### 🥕 **Product Model** (Produkty spożywcze)
```python
class Product(Base):
    __tablename__ = "products"
    
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # warzywa, mięso, nabiał, etc.
    unit = Column(String(20), nullable=False)  # kg, szt, l, etc.
    price_per_unit = Column(Float, nullable=True)
    calories_per_100g = Column(Integer, nullable=True)
    proteins = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### 📝 **Recipe Model** (Przepisy)
```python
class Recipe(Base):
    __tablename__ = "recipes"
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    ingredients = Column(JSON, nullable=False)  # lista składników z ilościami
    instructions = Column(Text, nullable=False)
    cooking_time = Column(Integer, nullable=True)  # w minutach
    difficulty = Column(String(20), nullable=True)  # łatwy, średni, trudny
    servings = Column(Integer, nullable=True)
    calories_per_serving = Column(Integer, nullable=True)
    tags = Column(JSON, nullable=True)  # kuchnia włoska, wegetariańska, etc.
    user_id = Column(Integer, ForeignKey("users.id"))
    is_ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### 🛒 **ShoppingList Model** (Lista zakupów)
```python
class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    
    name = Column(String(100), nullable=False)
    items = Column(JSON, nullable=False)  # lista produktów z ilościami
    total_estimated_cost = Column(Float, nullable=True)
    is_completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 🔌 NOWE API ENDPOINTS

#### 🥕 **Product Management** (`/api/v2/cooking/products`)
```python
@router.post("/add")           # Dodaj produkt
@router.get("/list")           # Lista produktów
@router.get("/categories")     # Kategorie produktów
@router.put("/{product_id}")   # Edytuj produkt
@router.delete("/{product_id}") # Usuń produkt
@router.post("/scan")          # Skanuj paragon/etykietę OCR
@router.get("/search")         # Wyszukaj produkty
```

#### 📝 **Recipe Management** (`/api/v2/cooking/recipes`)
```python
@router.post("/generate")              # Generuj przepis z AI
@router.post("/save")                  # Zapisz przepis
@router.get("/list")                   # Lista przepisów
@router.get("/{recipe_id}")            # Szczegóły przepisu
@router.post("/search")                # Wyszukaj przepisy
@router.post("/from-ingredients")      # Przepis z dostępnych składników
@router.post("/optimize")              # Optymalizuj przepis (AI)
@router.delete("/{recipe_id}")         # Usuń przepis
```

#### 🛒 **Shopping List** (`/api/v2/cooking/shopping`)
```python
@router.post("/create")                # Utwórz listę zakupów
@router.post("/from-recipe")           # Lista z przepisu
@router.post("/optimize")              # Optymalizuj listę (AI)
@router.get("/list")                   # Lista zakupów
@router.put("/{list_id}/complete")     # Oznacz jako zakończone
@router.delete("/{list_id}")           # Usuń listę
@router.get("/{list_id}/cost")         # Szacowanie kosztów
```

### 🎨 NOWE STRONY FRONTEND

#### 🍳 **Cooking Dashboard** (`/cooking`)
- **Quick Actions:**
  - "Dodaj produkt" (ręcznie lub skan)
  - "Generuj przepis" (AI)
  - "Utwórz listę zakupów"
  - "Przeglądaj przepisy"
- **Stats:**
  - Liczba produktów w bazie
  - Liczba przepisów
  - Ostatnie listy zakupów
  - Wydatki na jedzenie

#### 📱 **Product Management** (`/cooking/products`)
- Dodawanie produktów (ręcznie + OCR)
- Kategorie produktów
- Ceny i wartości odżywcze
- Skanowanie paragonów
- Wyszukiwanie produktów

#### 📖 **Recipe Page** (`/cooking/recipes`)
- Generowanie przepisów AI
- Zapisywanie ulubionych
- Wyszukiwanie przepisów
- Przepisy z dostępnych składników
- Edycja i usuwanie przepisów

#### 🛒 **Shopping List** (`/cooking/shopping`)
- Tworzenie list zakupów
- Optymalizacja przez AI
- Szacowanie kosztów
- Oznaczanie jako kupione
- Historia list zakupów

## 🤖 AI FUNKCJONALNOŚCI

### 📝 **Recipe Generation AI**
```python
async def generate_recipe_from_ingredients(ingredients: List[str], preferences: str = "") -> Recipe:
    """Generuj przepis z dostępnych składników."""
    prompt = f"""
    Stwórz przepis kulinarny używając następujących składników: {', '.join(ingredients)}
    
    Preferencje: {preferences}
    
    Odpowiedz w formacie JSON:
    {{
        "name": "Nazwa przepisu",
        "description": "Krótki opis",
        "ingredients": [{{"name": "nazwa", "amount": "ilość", "unit": "jednostka"}}],
        "instructions": "Kroki przygotowania",
        "cooking_time": 30,
        "difficulty": "łatwy",
        "servings": 4,
        "calories_per_serving": 250,
        "tags": ["kuchnia polska", "wegetariańska"]
    }}
    """
    
    response = await llm_factory.chat_with_fallback(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return Recipe(**json.loads(response["text"]))
```

### 🛒 **Shopping List Optimization**
```python
async def optimize_shopping_list(products: List[dict], budget: float = None) -> dict:
    """Optymalizuj listę zakupów przez AI."""
    prompt = f"""
    Zoptymalizuj listę zakupów:
    Produkty: {products}
    Budżet: {budget}
    
    Uwzględnij:
    - Najlepsze ceny
    - Sezonowość produktów
    - Zamienniki tańsze
    - Minimalizację odpadów
    - Promocje i zniżki
    """
    
    # AI optimization logic
    return optimized_list
```

### 🥕 **Product Recognition from OCR**
```python
async def extract_product_from_receipt(image_data: bytes) -> List[Product]:
    """Wyciągnij produkty z paragonu przez OCR."""
    # OCR text extraction
    ocr_result = await ocr_provider.extract_text(image_data)
    
    # AI parsing of receipt
    prompt = f"""
    Przeanalizuj paragon i wyciągnij produkty:
    {ocr_result}
    
    Odpowiedz w formacie JSON:
    [{{
        "name": "nazwa produktu",
        "quantity": "ilość",
        "unit": "jednostka",
        "price": "cena"
    }}]
    """
    
    # Parse products from OCR
    return products
```

## 🔗 INTEGRACJA Z OBECNYMI FUNKCJONALNOŚCIAMI

### 📷 **OCR dla produktów**
- Skanowanie paragonów → automatyczne dodawanie produktów
- Skanowanie etykiet → wartości odżywcze
- Skanowanie przepisów → konwersja na format cyfrowy

### 🔍 **Vector Store dla przepisów**
- Indeksowanie przepisów
- Wyszukiwanie semantyczne
- Rekomendacje podobnych przepisów

### 🎮 **Gamification dla gotowania**
- Osiągnięcia: "Mistrz kuchni", "Zdrowy styl życia", "Oszczędny kucharz"
- Punkty za dodawanie produktów, tworzenie przepisów
- Wyzwania: "Przygotuj 5 przepisów w tygodniu", "Zostań w budżecie"

### 💬 **Chat AI dla gotowania**
- Pytania o przepisy
- Porady kulinarne
- Substytuty składników
- Kalkulacje kalorii

## 📊 SCHEMATY PYDANTIC

### 🥕 **Product Schemas**
```python
class ProductCreate(BaseModel):
    name: str
    category: str
    unit: str
    price_per_unit: Optional[float] = None
    calories_per_100g: Optional[int] = None
    proteins: Optional[float] = None
    carbs: Optional[float] = None
    fats: Optional[float] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    unit: str
    price_per_unit: Optional[float]
    calories_per_100g: Optional[int]
    proteins: Optional[float]
    carbs: Optional[float]
    fats: Optional[float]
    created_at: datetime
```

### 📝 **Recipe Schemas**
```python
class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: List[Dict[str, Any]]
    instructions: str
    cooking_time: Optional[int] = None
    difficulty: Optional[str] = None
    servings: Optional[int] = None
    calories_per_serving: Optional[int] = None
    tags: Optional[List[str]] = None

class RecipeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    ingredients: List[Dict[str, Any]]
    instructions: str
    cooking_time: Optional[int]
    difficulty: Optional[str]
    servings: Optional[int]
    calories_per_serving: Optional[int]
    tags: Optional[List[str]]
    is_ai_generated: bool
    created_at: datetime
```

### 🛒 **Shopping List Schemas**
```python
class ShoppingListCreate(BaseModel):
    name: str
    items: List[Dict[str, Any]]
    budget: Optional[float] = None

class ShoppingListResponse(BaseModel):
    id: int
    name: str
    items: List[Dict[str, Any]]
    total_estimated_cost: Optional[float]
    is_completed: bool
    created_at: datetime
```

## 🎨 UI/UX DESIGN

### 🎨 **Kolory i motywy**
- **Primary:** Kolor pomarańczowy (#FF6B35) - symbolizuje gotowanie
- **Secondary:** Zielony (#4CAF50) - świeże produkty
- **Accent:** Czerwony (#F44336) - przyprawy i intensywność
- **Background:** Jasny beż (#FFF8E1) - ciepło kuchni

### 📱 **Komponenty UI**
- **Product Card:** Karta produktu z ceną i wartościami odżywczymi
- **Recipe Card:** Karta przepisu z czasem i trudnością
- **Shopping List:** Interaktywna lista z checkboxami
- **Ingredient Input:** Inteligentne pole wprowadzania składników
- **Cost Calculator:** Kalkulator kosztów w czasie rzeczywistym

### 🎯 **User Experience**
- **Intuitive Navigation:** Łatwe przełączanie między sekcjami
- **Quick Actions:** Szybkie dodawanie produktów i przepisów
- **Smart Suggestions:** AI podpowiedzi podczas wprowadzania danych
- **Visual Feedback:** Animacje i przejścia
- **Mobile First:** Responsywny design

## 🧪 TESTING STRATEGY

### 🔬 **Unit Tests**
- Testy modeli bazy danych
- Testy schematów Pydantic
- Testy funkcji AI
- Testy endpointów API

### 🔗 **Integration Tests**
- Testy przepływu dodawania produktów
- Testy generowania przepisów
- Testy optymalizacji list zakupów
- Testy integracji z OCR

### 🎨 **UI Tests**
- Testy komponentów React
- Testy nawigacji
- Testy formularzy
- Testy responsywności

## 📈 ROADMAP IMPLEMENTACJI

### **Faza 1: Podstawy (Tydzień 1)**
- [ ] Modele bazy danych (Product, Recipe, ShoppingList)
- [ ] Migracje bazy danych
- [ ] Podstawowe schematy Pydantic
- [ ] Podstawowe endpointy API

### **Faza 2: Backend AI (Tydzień 2)**
- [ ] Recipe generation AI
- [ ] Shopping list optimization
- [ ] Product recognition from OCR
- [ ] Integration z istniejącymi providerami

### **Faza 3: Frontend (Tydzień 3)**
- [ ] Cooking Dashboard
- [ ] Product Management Page
- [ ] Recipe Page
- [ ] Shopping List Page

### **Faza 4: Integracja i Polish (Tydzień 4)**
- [ ] Integracja z gamification
- [ ] Integracja z OCR
- [ ] UI/UX improvements
- [ ] Testing i bug fixes

### **Faza 5: Optymalizacja (Tydzień 5)**
- [ ] Performance optimization
- [ ] Advanced AI features
- [ ] User feedback implementation
- [ ] Documentation

## 🎯 KORZYŚCI DLA ANTONINY

### 📱 **Łatwość użytkowania**
- Intuicyjny interfejs
- Szybkie dodawanie produktów
- Automatyczne kalkulacje

### 🤖 **AI Assistance**
- Generowanie przepisów z dostępnych składników
- Optymalizacja list zakupów
- Inteligentne podpowiedzi

### 💰 **Kontrola finansowa**
- Śledzenie wydatków na jedzenie
- Optymalizacja budżetu
- Historia zakupów

### 🥗 **Zdrowy styl życia**
- Śledzenie wartości odżywczych
- Różnorodność przepisów
- Planowanie posiłków

### 🎮 **Motywacja**
- System punktów i osiągnięć
- Wyzwania kulinarne
- Postęp w gotowaniu

## 📊 METRYKI SUKCESU

### 📈 **Użytkowanie**
- Liczba dodanych produktów
- Liczba wygenerowanych przepisów
- Liczba utworzonych list zakupów
- Czas spędzony w aplikacji

### 💰 **Oszczędności**
- Redukcja wydatków na jedzenie
- Mniej marnowania produktów
- Optymalizacja zakupów

### 🎯 **Satysfakcja użytkownika**
- Oceny przepisów
- Feedback w aplikacji
- Retention rate

## 🔮 PRZYSZŁE ROZSZERZENIA

### 🌍 **Social Features**
- Udostępnianie przepisów
- Społeczność kucharzy
- Rating przepisów

### 📊 **Analytics**
- Szczegółowe analizy wydatków
- Trendy żywieniowe
- Rekomendacje personalne

### 🛒 **E-commerce Integration**
- Integracja z sklepami online
- Automatyczne zamawianie
- Porównywanie cen

### 📱 **Mobile App**
- Nativna aplikacja mobilna
- Push notifications
- Offline mode

---

**Status:** 📋 Plan gotowy do implementacji  
**Następny krok:** Commity dokumentacji → Implementacja Fazy 1
