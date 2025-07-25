#!/bin/bash

# Deploy script for Crypto Market Alert System
# Usage: ./deploy.sh [production|staging]

set -e

ENV=${1:-staging}
echo "🚀 Deploying Crypto Market Alert to $ENV..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_warning "Copy config/example.env to .env and configure your credentials"
    exit 1
fi

# Check if Python requirements are installed
print_status "Checking Python dependencies..."
if ! python -c "import requests, pandas, asyncio" 2>/dev/null; then
    print_warning "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Run tests
print_status "Running tests..."
python test_strategic_message.py || {
    print_error "Strategic message test failed!"
    exit 1
}

python test_hybrid_fetcher.py || {
    print_error "Hybrid fetcher test failed!"
    exit 1
}

print_status "All tests passed! ✅"

# Production deployment
if [ "$ENV" = "production" ]; then
    print_status "Deploying to PRODUCTION..."
    
    # Install systemd service
    if [ -f "scripts/install_service.sh" ]; then
        print_status "Installing systemd service..."
        sudo bash scripts/install_service.sh
    fi
    
    # Start the service
    print_status "Starting crypto-alert service..."
    sudo systemctl enable crypto-alert
    sudo systemctl start crypto-alert
    sudo systemctl status crypto-alert
    
    print_status "🎉 Production deployment complete!"
    print_warning "Monitor logs with: sudo journalctl -u crypto-alert -f"
    
else
    # Staging deployment (just run locally)
    print_status "Starting in STAGING mode..."
    python main.py
fi
