#!/bin/bash

# Complete installation and setup script for Salah Times Tray
# This script builds the AppImage and sets up autostart in one go

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🕌 Salah Times Tray - Complete Installation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Please don't run this script as root."
    echo "   It will ask for sudo permissions when needed."
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    echo "   Install with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Check pip
if ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip is required but not installed."
    echo "   Install with: sudo apt install python3-pip"
    exit 1
fi

# Check wget
if ! command -v wget &> /dev/null; then
    echo "❌ wget is required but not installed."
    echo "   Install with: sudo apt install wget"
    exit 1
fi

echo "✅ All dependencies found!"
echo ""

# Build AppImage
echo "🔨 Building AppImage..."
if [ ! -f "./build_tray_appimage.sh" ]; then
    echo "❌ build_tray_appimage.sh not found!"
    exit 1
fi

chmod +x ./build_tray_appimage.sh
./build_tray_appimage.sh

# Check if AppImage was created
APPIMAGE_NAME="SalahTimesTray-1.0-x86_64.AppImage"
if [ ! -f "$APPIMAGE_NAME" ]; then
    echo "❌ AppImage build failed!"
    exit 1
fi

echo ""
echo "✅ AppImage built successfully!"
echo ""

# Ask user for installation preference
echo "📦 Installation Options:"
echo "  1) System-wide (all users) - requires sudo"
echo "  2) User-only (current user only)"
echo "  3) Skip installation (just build AppImage)"
echo ""

while true; do
    read -p "Choose installation type (1/2/3): " choice
    case $choice in
        1)
            echo ""
            echo "🔧 Setting up system-wide installation..."
            chmod +x ./setup_system_autostart.sh
            ./setup_system_autostart.sh
            break
            ;;
        2)
            echo ""
            echo "👤 Setting up user installation..."
            chmod +x ./setup_user_autostart.sh
            ./setup_user_autostart.sh
            break
            ;;
        3)
            echo ""
            echo "⏭️  Skipping installation setup."
            echo "   You can run the AppImage manually: ./$APPIMAGE_NAME"
            break
            ;;
        *)
            echo "Please enter 1, 2, or 3."
            ;;
    esac
done

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "📋 What's been installed:"
echo "  • Salah Times Tray AppImage"
echo "  • System tray indicator with prayer notifications"
echo "  • Iqama countdown alerts (2 minutes before end)"
echo "  • Auto-start on system boot/login"
echo ""
echo "🚀 Usage:"
echo "  • The tray indicator should start automatically on next login"
echo "  • Right-click the tray icon to see all prayer times"
echo "  • Left-click or hover to see next prayer countdown"
echo "  • Notifications will appear at prayer times and Iqama warnings"
echo ""
echo "💡 Manual control:"
if [ "$choice" = "1" ]; then
    echo "  • Start: /usr/local/bin/SalahTimesTray &"
    echo "  • Stop: pkill -f SalahTimesTray"
elif [ "$choice" = "2" ]; then
    echo "  • Start: ~/.local/bin/SalahTimesTray &"
    echo "  • Stop: pkill -f SalahTimesTray"
else
    echo "  • Start: ./$APPIMAGE_NAME &"
    echo "  • Stop: pkill -f SalahTimesTray"
fi
echo ""
echo "🔧 Configuration:"
echo "  • Settings are shared with the main Salah Times app"
echo "  • Right-click tray → Settings to open main app"
echo "  • Config file: ~/.salah_config.json"
echo ""
echo "🔄 To start now without rebooting:"
if [ "$choice" = "1" ]; then
    echo "   /usr/local/bin/SalahTimesTray &"
elif [ "$choice" = "2" ]; then
    echo "   ~/.local/bin/SalahTimesTray &"
else
    echo "   ./$APPIMAGE_NAME &"
fi
echo ""
echo "📖 For more information, see: TRAY_INDICATOR_README.md"