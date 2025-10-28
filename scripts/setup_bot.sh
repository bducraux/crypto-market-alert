#!/bin/bash
# Quick Start Guide for Telegram Bot Setup

echo "🚀 Crypto Portfolio Telegram Bot - Quick Start"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "telegram_bot.py" ]; then
    echo "❌ Error: Run this script from the project root directory"
    exit 1
fi

echo "📋 Step 1: Create Telegram Bot"
echo "   1. Open Telegram and search for @BotFather"
echo "   2. Send: /newbot"
echo "   3. Follow instructions to create your bot"
echo "   4. Copy the Bot Token"
echo ""
read -p "Press Enter when you have your Bot Token..."
echo ""

echo "📋 Step 2: Get Your Chat ID"
echo "   1. Search for @userinfobot on Telegram"
echo "   2. Start the bot"
echo "   3. Copy your Chat ID (the number shown)"
echo ""
read -p "Press Enter when you have your Chat ID..."
echo ""

echo "📋 Step 3: Configure .env file"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    if [ -f "config/example.env" ]; then
        cp config/example.env .env
    else
        touch .env
    fi
fi

# Read credentials
echo "Enter your Telegram Bot Token:"
read -r BOT_TOKEN

echo "Enter your Telegram Chat ID:"
read -r CHAT_ID

# Update or add to .env
if grep -q "TELEGRAM_BOT_TOKEN=" .env; then
    sed -i "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$BOT_TOKEN|" .env
else
    echo "TELEGRAM_BOT_TOKEN=$BOT_TOKEN" >> .env
fi

if grep -q "TELEGRAM_CHAT_ID=" .env; then
    sed -i "s|TELEGRAM_CHAT_ID=.*|TELEGRAM_CHAT_ID=$CHAT_ID|" .env
else
    echo "TELEGRAM_CHAT_ID=$CHAT_ID" >> .env
fi

echo "✅ .env file updated"
echo ""

echo "📋 Step 4: Install Dependencies"
if [ -d "venv" ]; then
    echo "Virtual environment found, activating..."
    source venv/bin/activate
    pip install -q python-telegram-bot
    echo "✅ Dependencies installed"
else
    echo "⚠️  Virtual environment not found!"
    echo "   Run: python -m venv venv && source venv/bin/activate"
    echo "   Then: pip install -r requirements.txt"
fi
echo ""

echo "📋 Step 5: Test the Bot"
echo ""
read -p "Would you like to test the bot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🧪 Starting bot in test mode..."
    echo "   Press Ctrl+C to stop"
    echo "   Send /start to your bot on Telegram"
    echo ""
    sleep 2
    python telegram_bot.py
fi

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📖 Next Steps:"
echo "   1. Install as service: ./scripts/install_bot_service.sh"
echo "   2. Or run manually: python telegram_bot.py"
echo "   3. Read full docs: docs/TELEGRAM_BOT.md"
echo ""
echo "💡 Send /start to your bot on Telegram to begin!"

