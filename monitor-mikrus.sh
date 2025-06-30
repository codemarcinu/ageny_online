#!/bin/bash

# 📊 Ageny Online - Skrypt monitorowania na Mikrus
# Autor: Marcin C.
# Data: 2025-01-29

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

# Sprawdzenie statusu kontenerów
check_containers() {
    echo "🐳 Status kontenerów:"
    echo "===================="
    
    docker-compose -f docker-compose.mikrus.yaml ps
    
    echo ""
}

# Sprawdzenie zasobów
check_resources() {
    echo "💾 Zasoby systemowe:"
    echo "==================="
    
    # CPU i RAM
    echo "CPU i RAM:"
    free -h
    echo ""
    
    # Dysk
    echo "Dysk:"
    df -h
    echo ""
    
    # Docker stats
    echo "Docker stats (ostatnie 10 sekund):"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    echo ""
}

# Sprawdzenie logów
check_logs() {
    echo "📝 Ostatnie logi (ostatnie 10 linii):"
    echo "===================================="
    
    echo "Backend:"
    docker-compose -f docker-compose.mikrus.yaml logs --tail=10 backend
    echo ""
    
    echo "Redis:"
    docker-compose -f docker-compose.mikrus.yaml logs --tail=10 redis
    echo ""
    
    echo "Nginx:"
    docker-compose -f docker-compose.mikrus.yaml logs --tail=10 nginx
    echo ""
}

# Sprawdzenie health check
check_health() {
    echo "🏥 Health check:"
    echo "==============="
    
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend API działa poprawnie"
        
        # Pobranie szczegółów health check
        HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
        echo "Szczegóły: $HEALTH_RESPONSE"
    else
        print_error "Backend API nie odpowiada!"
    fi
    
    echo ""
}

# Sprawdzenie endpointów
check_endpoints() {
    echo "🔗 Test endpointów:"
    echo "=================="
    
    ENDPOINTS=(
        "https://joanna114.mikrus.xyz"
        "https://joanna114.mikrus.xyz/health"
        "https://joanna114.mikrus.xyz/docs"
    )
    
    for endpoint in "${ENDPOINTS[@]}"; do
        if curl -f -s "$endpoint" > /dev/null 2>&1; then
            print_success "$endpoint - OK"
        else
            print_error "$endpoint - BŁĄD"
        fi
    done
    
    echo ""
}

# Sprawdzenie połączeń sieciowych
check_network() {
    echo "🌐 Połączenia sieciowe:"
    echo "======================"
    
    # Porty
    echo "Porty nasłuchujące:"
    netstat -tlnp | grep -E ':(80|443|8000|6379)' || echo "Brak aktywnych połączeń"
    echo ""
    
    # Połączenia Docker
    echo "Połączenia Docker:"
    docker network ls
    echo ""
}

# Sprawdzenie bezpieczeństwa
check_security() {
    echo "🔒 Bezpieczeństwo:"
    echo "================="
    
    # Sprawdzenie certyfikatu SSL
    if [ -f "ssl/cert.pem" ]; then
        print_success "Certyfikat SSL istnieje"
        echo "Ważność certyfikatu:"
        openssl x509 -in ssl/cert.pem -text -noout | grep -E "(Not Before|Not After)"
    else
        print_warning "Certyfikat SSL nie istnieje"
    fi
    
    echo ""
    
    # Sprawdzenie firewall
    echo "Status firewall:"
    ufw status
    echo ""
}

# Backup danych
backup_data() {
    echo "💾 Backup danych:"
    echo "================"
    
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup bazy danych
    if [ -d "data" ]; then
        cp -r data "$BACKUP_DIR/"
        print_success "Backup bazy danych utworzony: $BACKUP_DIR/data"
    fi
    
    # Backup logów
    if [ -d "logs" ]; then
        cp -r logs "$BACKUP_DIR/"
        print_success "Backup logów utworzony: $BACKUP_DIR/logs"
    fi
    
    # Backup konfiguracji
    cp .env.online "$BACKUP_DIR/" 2>/dev/null || true
    print_success "Backup konfiguracji utworzony: $BACKUP_DIR/.env.online"
    
    echo ""
}

# Główna funkcja monitorowania
main() {
    echo "📊 Ageny Online - Monitoring na Mikrus"
    echo "======================================"
    echo "Data: $(date)"
    echo ""
    
    check_containers
    check_resources
    check_logs
    check_health
    check_endpoints
    check_network
    check_security
    
    # Backup co godzinę
    if [ "$1" = "--backup" ]; then
        backup_data
    fi
    
    echo "✅ Monitoring zakończony"
}

# Uruchomienie głównej funkcji
main "$@" 