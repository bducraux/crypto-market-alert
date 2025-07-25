#!/bin/bash

# Crypto Market Alert System Setup Script
# This script helps set up the project environment

set -e  # Exit on any error

echo "🚀 Setting up Crypto Market Alert System..."

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d" " -f2 | cut -d"." -f1-2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version is compatible (>= $required_version)"
else
    echo "❌ Python $python_version is not compatible. Please install Python >= $required_version"
    exit 1
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
echo "⚙️  Setting up environment file..."
if [ ! -f ".env" ]; then
    cp config/example.env .env
    echo "✅ Created .env file from template"
    echo "🔑 Please edit .env file with your API keys and tokens"
else
    echo "⚠️  .env file already exists"
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs
touch logs/.gitkeep

# Set executable permissions for run script
echo "🔐 Setting permissions..."
chmod +x run.py

# Test installation
echo "🧪 Testing installation..."
python -c "
import sys
print('✅ Python path:', sys.executable)

# Test required imports
try:
    import requests
    import pandas
    import yaml
    import telegram
    print('✅ All required packages installed successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit the .env file with your Telegram bot token and chat ID"
echo "   2. Edit config/config.yaml to customize your monitoring settings"
echo "   3. Run 'python run.py --test' to test your configuration"
echo "   4. Run 'python run.py --once' for a single market check"
echo "   5. Run 'python run.py' to start continuous monitoring"
echo ""
echo "📚 For detailed setup instructions, see README.md"
