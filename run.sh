#!/bin/bash

# Ageny Online - Startup Script
# Przekształcenie FoodSave AI na wersję online

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3.8+ is required but not installed."
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $python_version found"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Check configuration
check_config() {
    if [ ! -f ".env.online" ]; then
        print_warning "Configuration file .env.online not found!"
        print_status "Please copy env.example to .env.online and configure your API keys:"
        echo "  cp env.example .env.online"
        echo "  nano .env.online"
        echo ""
        print_status "Minimum required configuration:"
        echo "  OPENAI_API_KEY=your_openai_api_key_here"
        echo ""
        read -p "Do you want to continue without configuration? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "Configuration file found"
    fi
}

# Setup providers
setup_providers() {
    print_status "Setting up providers..."
    python3 -c "
import asyncio
import sys
sys.path.append('src')
from backend.api.main import setup_providers
import uvicorn
from fastapi.testclient import TestClient
from backend.api.main import app

async def setup():
    client = TestClient(app)
    response = client.post('/api/v1/setup')
    if response.status_code == 200:
        print('Providers configured successfully')
    else:
        print('Failed to configure providers')

asyncio.run(setup())
"
}

# Health check
health_check() {
    print_status "Performing health check..."
    python3 -c "
import requests
import time

def check_health():
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print('✅ Health check passed')
            print(f'   Status: {data.get(\"status\")}')
            print(f'   LLM Providers: {list(data.get(\"llm_providers\", []))}')
            print(f'   OCR Providers: {list(data.get(\"ocr_providers\", []))}')
            return True
        else:
            print(f'❌ Health check failed: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Health check failed: {e}')
        return False

# Wait for server to start
for i in range(10):
    time.sleep(1)
    if check_health():
        break
"
}

# Main function
main() {
    echo "🚀 Ageny Online - Starting up..."
    echo "=================================="
    
    # Check prerequisites
    check_python
    check_venv
    activate_venv
    install_dependencies
    check_config
    
    # Setup providers
    setup_providers
    
    print_status "Starting Ageny Online API server..."
    print_status "API Documentation will be available at: http://localhost:8000/docs"
    print_status "Health check: http://localhost:8000/health"
    print_status "Press Ctrl+C to stop the server"
    echo ""
    
    # Start the server
    uvicorn src.backend.api.main:app --host 0.0.0.0 --port 8000 --reload
}

# Handle script arguments
case "${1:-}" in
    "install")
        check_python
        check_venv
        activate_venv
        install_dependencies
        print_success "Installation completed!"
        ;;
    "setup")
        check_venv
        activate_venv
        setup_providers
        ;;
    "health")
        health_check
        ;;
    "help"|"-h"|"--help")
        echo "Ageny Online - Startup Script"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  install    Install dependencies only"
        echo "  setup      Setup providers only"
        echo "  health     Perform health check"
        echo "  help       Show this help message"
        echo ""
        echo "Without arguments, starts the full application"
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 