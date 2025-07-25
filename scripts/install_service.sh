#!/bin/bash

# Systemd service installation script for Crypto Market Alert System

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="crypto-alert"

echo "🔧 Installing Crypto Market Alert System as systemd service..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root"
    echo "   Run as your regular user, we'll use sudo when needed"
    exit 1
fi

# Get current user and group
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)

echo "📋 Configuration:"
echo "   User: $CURRENT_USER"
echo "   Group: $CURRENT_GROUP"
echo "   Project directory: $PROJECT_DIR"
echo "   Service name: $SERVICE_NAME"

# Create service file with correct paths
SERVICE_FILE="/tmp/$SERVICE_NAME.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Crypto Market Alert System
After=network.target
Wants=network.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_GROUP
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/run.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=crypto-alert

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$PROJECT_DIR/logs

[Install]
WantedBy=multi-user.target
EOF

# Install service file
echo "📦 Installing service file..."
sudo cp "$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"
sudo systemctl daemon-reload

echo "✅ Service installed successfully!"
echo ""
echo "🎛️  Service management commands:"
echo "   sudo systemctl enable $SERVICE_NAME    # Enable auto-start on boot"
echo "   sudo systemctl start $SERVICE_NAME     # Start the service"
echo "   sudo systemctl stop $SERVICE_NAME      # Stop the service"
echo "   sudo systemctl restart $SERVICE_NAME   # Restart the service"
echo "   sudo systemctl status $SERVICE_NAME    # Check service status"
echo "   journalctl -u $SERVICE_NAME -f         # View live logs"
echo ""
echo "⚠️  Before starting the service:"
echo "   1. Make sure your .env file is properly configured"
echo "   2. Test the system with: python run.py --test"
echo "   3. Enable and start: sudo systemctl enable $SERVICE_NAME && sudo systemctl start $SERVICE_NAME"

# Clean up
rm "$SERVICE_FILE"
