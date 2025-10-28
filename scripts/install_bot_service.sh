#!/bin/bash
# Installation script for Crypto Portfolio Telegram Bot service

set -e

echo "🤖 Crypto Portfolio Telegram Bot Service Installer"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo "❌ Please do not run this script as root"
   echo "   Run it as your regular user. The script will ask for sudo when needed."
   exit 1
fi

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📁 Project directory: $PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run setup.sh first to create the virtual environment."
    exit 1
fi

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "❌ .env file not found!"
    echo "   Please create .env file with TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
    exit 1
fi

# Verify Telegram credentials
echo ""
echo "🔍 Verifying Telegram credentials..."
if ! grep -q "TELEGRAM_BOT_TOKEN=" "$PROJECT_DIR/.env"; then
    echo "❌ TELEGRAM_BOT_TOKEN not found in .env file"
    exit 1
fi

if ! grep -q "TELEGRAM_CHAT_ID=" "$PROJECT_DIR/.env"; then
    echo "❌ TELEGRAM_CHAT_ID not found in .env file"
    exit 1
fi

echo "✅ Telegram credentials found"

# Get current user and group
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)

echo ""
echo "👤 Service will run as: $CURRENT_USER:$CURRENT_GROUP"

# Create service file
SERVICE_FILE="crypto-bot.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_FILE"
TEMP_SERVICE="/tmp/$SERVICE_FILE"

echo ""
echo "📝 Creating service file..."

# Copy and modify the service template
sed -e "s|YOUR_USERNAME|$CURRENT_USER|g" \
    -e "s|YOUR_GROUP|$CURRENT_GROUP|g" \
    -e "s|/path/to/crypto-market-alert|$PROJECT_DIR|g" \
    "$PROJECT_DIR/scripts/crypto-bot.service" > "$TEMP_SERVICE"

# Show the service file content
echo ""
echo "Service configuration:"
echo "====================="
cat "$TEMP_SERVICE"
echo "====================="
echo ""

# Ask for confirmation
read -p "Install this service? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Installation cancelled"
    rm "$TEMP_SERVICE"
    exit 1
fi

# Install the service
echo ""
echo "🔧 Installing service..."
sudo mv "$TEMP_SERVICE" "$SERVICE_PATH"
sudo chmod 644 "$SERVICE_PATH"

# Reload systemd
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service
echo "✅ Enabling service..."
sudo systemctl enable $SERVICE_FILE

# Ask if user wants to start now
echo ""
read -p "Start the bot service now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting service..."
    sudo systemctl start $SERVICE_FILE

    # Wait a moment for service to start
    sleep 2

    # Check status
    echo ""
    echo "📊 Service status:"
    sudo systemctl status $SERVICE_FILE --no-pager || true
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Useful commands:"
echo "   Start bot:     sudo systemctl start $SERVICE_FILE"
echo "   Stop bot:      sudo systemctl stop $SERVICE_FILE"
echo "   Restart bot:   sudo systemctl restart $SERVICE_FILE"
echo "   View status:   sudo systemctl status $SERVICE_FILE"
echo "   View logs:     sudo journalctl -u $SERVICE_FILE -f"
echo "   Disable:       sudo systemctl disable $SERVICE_FILE"
echo ""
echo "💡 The bot will now run automatically on system startup!"
echo "   Send /start to your Telegram bot to begin using it."

