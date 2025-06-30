#!/bin/bash

# 🚀 Ageny Online - Skrypt wdrożenia na Mikrus
# Autor: Marcin C.
# Data: 2025-01-29

set -e

# Kolory dla output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funkcje pomocnicze
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Sprawdzenie wymagań
check_requirements() {
    print_status "Sprawdzanie wymagań systemowych..."
    
    # Sprawdzenie Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker nie jest zainstalowany!"
        exit 1
    fi
    
    # Sprawdzenie Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose nie jest zainstalowany!"
        exit 1
    fi
    
    # Sprawdzenie pliku konfiguracyjnego
    if [ ! -f ".env.online" ]; then
        print_warning "Plik .env.online nie istnieje!"
        print_status "Kopiowanie z przykładu..."
        cp env.example .env.online
        print_warning "Edytuj plik .env.online i dodaj klucze API przed kontynuacją!"
        exit 1
    fi
    
    print_success "Wszystkie wymagania spełnione"
}

# Tworzenie katalogów
create_directories() {
    print_status "Tworzenie katalogów..."
    
    mkdir -p data logs config ssl
    
    # Tworzenie certyfikatu SSL (self-signed)
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        print_status "Generowanie certyfikatu SSL..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem \
            -out ssl/cert.pem \
            -subj "/C=PL/ST=Poland/L=Warsaw/O=Ageny Online/CN=joanna114.mikrus.xyz"
    fi
    
    print_success "Katalogi utworzone"
}

# Zatrzymanie istniejących kontenerów
stop_existing() {
    print_status "Zatrzymywanie istniejących kontenerów..."
    
    docker-compose -f docker-compose.mikrus.yaml down --remove-orphans 2>/dev/null || true
    
    print_success "Istniejące kontenery zatrzymane"
}

# Budowanie i uruchamianie
build_and_start() {
    print_status "Budowanie obrazów Docker..."
    
    docker-compose -f docker-compose.mikrus.yaml build --no-cache
    
    print_status "Uruchamianie kontenerów..."
    
    docker-compose -f docker-compose.mikrus.yaml up -d
    
    print_success "Kontenery uruchomione"
}

# Sprawdzenie statusu
check_status() {
    print_status "Sprawdzanie statusu aplikacji..."
    
    # Czekanie na uruchomienie
    sleep 10
    
    # Sprawdzenie kontenerów
    if docker-compose -f docker-compose.mikrus.yaml ps | grep -q "Up"; then
        print_success "Wszystkie kontenery działają"
    else
        print_error "Niektóre kontenery nie działają!"
        docker-compose -f docker-compose.mikrus.yaml ps
        exit 1
    fi
    
    # Sprawdzenie health check
    print_status "Sprawdzanie health check..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Health check przechodzi"
    else
        print_warning "Health check nie przechodzi - sprawdź logi"
    fi
}

# Wyświetlenie informacji
show_info() {
    echo ""
    echo "🎉 Ageny Online zostało wdrożone na Mikrus!"
    echo "=========================================="
    echo ""
    echo "📡 Endpointy:"
    echo "   API: https://joanna114.mikrus.xyz"
    echo "   Dokumentacja: https://joanna114.mikrus.xyz/docs"
    echo "   Health check: https://joanna114.mikrus.xyz/health"
    echo ""
    echo "🔧 Zarządzanie:"
    echo "   Logi: docker-compose -f docker-compose.mikrus.yaml logs -f"
    echo "   Restart: docker-compose -f docker-compose.mikrus.yaml restart"
    echo "   Stop: docker-compose -f docker-compose.mikrus.yaml down"
    echo ""
    echo "📊 Monitoring:"
    echo "   Kontenery: docker ps"
    echo "   Zasoby: docker stats"
    echo ""
}

# Główna funkcja
main() {
    echo "🚀 Ageny Online - Wdrażanie na Mikrus"
    echo "====================================="
    echo ""
    
    check_requirements
    create_directories
    stop_existing
    build_and_start
    check_status
    show_info
}

# Uruchomienie głównej funkcji
main "$@" 