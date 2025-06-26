#!/bin/bash

# Ageny Online - Test Runner Script

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

# Check if virtual environment exists and activate it
check_and_activate_venv() {
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install test dependencies
install_test_deps() {
    print_status "Installing test dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Test dependencies installed"
}

# Run specific test categories
run_unit_tests() {
    print_status "Running unit tests..."
    pytest tests/unit/ -v --cov=src --cov-report=term-missing
}

run_integration_tests() {
    print_status "Running integration tests..."
    pytest tests/integration/ -v --cov=src --cov-report=term-missing
}

run_llm_tests() {
    print_status "Running LLM provider tests..."
    pytest tests/unit/test_llm_providers.py -v -m llm
}

run_ocr_tests() {
    print_status "Running OCR provider tests..."
    pytest tests/unit/test_ocr_providers.py -v -m ocr
}

run_vector_store_tests() {
    print_status "Running vector store tests..."
    pytest tests/unit/test_vector_stores.py -v -m vector_store
}

run_config_tests() {
    print_status "Running configuration tests..."
    pytest tests/unit/test_config.py -v -m config
}

run_api_tests() {
    print_status "Running API tests..."
    pytest tests/integration/test_api_endpoints.py -v -m api
}

# Run all tests
run_all_tests() {
    print_status "Running all tests..."
    pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html:htmlcov
}

# Generate coverage report
generate_coverage_report() {
    print_status "Generating coverage report..."
    coverage html --directory=htmlcov
    print_success "Coverage report generated: htmlcov/index.html"
}

# Run tests with specific options
run_tests_with_options() {
    local options="$1"
    print_status "Running tests with options: $options"
    pytest tests/ -v $options
}

# Main function
main() {
    echo "🧪 Ageny Online - Test Runner"
    echo "============================="
    
    # Check and activate virtual environment
    check_and_activate_venv
    
    # Install dependencies
    install_test_deps
    
    # Parse command line arguments
    case "${1:-}" in
        "unit")
            run_unit_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "llm")
            run_llm_tests
            ;;
        "ocr")
            run_ocr_tests
            ;;
        "vector-store")
            run_vector_store_tests
            ;;
        "config")
            run_config_tests
            ;;
        "api")
            run_api_tests
            ;;
        "coverage")
            run_all_tests
            generate_coverage_report
            ;;
        "fast")
            run_tests_with_options "-x --tb=short"
            ;;
        "parallel")
            run_tests_with_options "-n auto"
            ;;
        "help"|"-h"|"--help")
            echo "Ageny Online - Test Runner"
            echo ""
            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  unit          Run unit tests only"
            echo "  integration   Run integration tests only"
            echo "  llm           Run LLM provider tests"
            echo "  ocr           Run OCR provider tests"
            echo "  vector-store  Run vector store tests"
            echo "  config        Run configuration tests"
            echo "  api           Run API tests"
            echo "  coverage      Run all tests with coverage report"
            echo "  fast          Run tests with fast fail"
            echo "  parallel      Run tests in parallel"
            echo "  help          Show this help message"
            echo ""
            echo "Without arguments, runs all tests"
            ;;
        "")
            run_all_tests
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
    
    print_success "Tests completed!"
}

# Run main function
main "$@" 