#!/bin/bash

# Setup user-specific autostart for Salah Times Tray
# This script sets up the tray indicator to start automatically for the current user only

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="SalahTimesTray"
APPIMAGE_NAME="$APP_NAME-1.0-x86_64.AppImage"
APPIMAGE_PATH="$SCRIPT_DIR/$APPIMAGE_NAME"

echo "👤 Setting up Salah Times Tray user autostart..."

# Check if AppImage exists
if [ ! -f "$APPIMAGE_PATH" ]; then
    echo "❌ AppImage not found: $APPIMAGE_PATH"
    echo "Please build the AppImage first by running: ./build_tray_appimage.sh"
    exit 1
fi

# Make AppImage executable
chmod +x "$APPIMAGE_PATH"

# Create user directories
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/applications
mkdir -p ~/.config/autostart

# Copy AppImage to user location
cp "$APPIMAGE_PATH" "$HOME/.local/bin/$APP_NAME"
chmod +x "$HOME/.local/bin/$APP_NAME"

# Add to PATH if not already there
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "📝 Added ~/.local/bin to PATH in ~/.bashrc"
fi

# Create user desktop file
cat > "$HOME/.local/share/applications/salah-times-tray.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Salah Times Tray
Comment=Islamic prayer times system tray indicator with notifications
Exec=$HOME/.local/bin/$APP_NAME
Icon=preferences-system-time
Terminal=false
Categories=Utility;
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

# Create autostart file for current user
cat > "$HOME/.config/autostart/salah-times-tray.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Salah Times Tray
Comment=Islamic prayer times system tray indicator
Exec=$HOME/.local/bin/$APP_NAME
Icon=preferences-system-time
Terminal=false
Categories=Utility;
StartupNotify=false
X-GNOME-Autostart-enabled=true
Hidden=false
NoDisplay=false
EOF

# Set proper permissions
chmod 644 "$HOME/.local/share/applications/salah-times-tray.desktop"
chmod 644 "$HOME/.config/autostart/salah-times-tray.desktop"

echo "✅ User installation complete!"
echo ""
echo "📋 Installation Summary:"
echo "  • AppImage installed to: $HOME/.local/bin/$APP_NAME"
echo "  • Desktop file: $HOME/.local/share/applications/salah-times-tray.desktop"
echo "  • Autostart file: $HOME/.config/autostart/salah-times-tray.desktop"
echo ""
echo "🚀 The tray indicator will now start automatically on your login."
echo ""
echo "💡 Manual control:"
echo "  • Start now: $HOME/.local/bin/$APP_NAME &"
echo "  • Stop: pkill -f $APP_NAME"
echo "  • Disable autostart: rm ~/.config/autostart/salah-times-tray.desktop"
echo ""
echo "🔄 Please log out and log back in, or restart your session to see the tray indicator."