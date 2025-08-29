#!/bin/bash

# Setup system-wide autostart for Salah Times Tray
# This script sets up the tray indicator to start automatically for all users

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="SalahTimesTray"
APPIMAGE_NAME="$APP_NAME-1.0-x86_64.AppImage"
APPIMAGE_PATH="$SCRIPT_DIR/$APPIMAGE_NAME"

echo "🔧 Setting up Salah Times Tray system autostart..."

# Check if AppImage exists
if [ ! -f "$APPIMAGE_PATH" ]; then
    echo "❌ AppImage not found: $APPIMAGE_PATH"
    echo "Please build the AppImage first by running: ./build_tray_appimage.sh"
    exit 1
fi

# Make AppImage executable
chmod +x "$APPIMAGE_PATH"

# Option 1: Install to system applications directory
echo "📦 Installing AppImage to system..."

# Create applications directory if it doesn't exist
sudo mkdir -p /usr/local/bin
sudo mkdir -p /usr/share/applications
sudo mkdir -p /etc/xdg/autostart

# Copy AppImage to system location
sudo cp "$APPIMAGE_PATH" "/usr/local/bin/$APP_NAME"
sudo chmod +x "/usr/local/bin/$APP_NAME"

# Create system desktop file
sudo tee "/usr/share/applications/salah-times-tray.desktop" > /dev/null << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Salah Times Tray
Comment=Islamic prayer times system tray indicator with notifications
Exec=/usr/local/bin/$APP_NAME
Icon=preferences-system-time
Terminal=false
Categories=Utility;System;
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

# Create autostart file for all users
sudo tee "/etc/xdg/autostart/salah-times-tray.desktop" > /dev/null << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Salah Times Tray
Comment=Islamic prayer times system tray indicator
Exec=/usr/local/bin/$APP_NAME
Icon=preferences-system-time
Terminal=false
Categories=Utility;
StartupNotify=false
X-GNOME-Autostart-enabled=true
Hidden=false
NoDisplay=false
EOF

# Set proper permissions
sudo chmod 644 "/usr/share/applications/salah-times-tray.desktop"
sudo chmod 644 "/etc/xdg/autostart/salah-times-tray.desktop"

echo "✅ System installation complete!"
echo ""
echo "📋 Installation Summary:"
echo "  • AppImage installed to: /usr/local/bin/$APP_NAME"
echo "  • Desktop file: /usr/share/applications/salah-times-tray.desktop"
echo "  • Autostart file: /etc/xdg/autostart/salah-times-tray.desktop"
echo ""
echo "🚀 The tray indicator will now start automatically for all users on login."
echo ""
echo "💡 Manual control:"
echo "  • Start now: /usr/local/bin/$APP_NAME &"
echo "  • Stop: pkill -f $APP_NAME"
echo "  • Disable autostart: sudo rm /etc/xdg/autostart/salah-times-tray.desktop"
echo ""
echo "🔧 User-specific setup (alternative):"
echo "  • Run: ./setup_user_autostart.sh (for current user only)"