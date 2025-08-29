#!/bin/bash

# Build Salah Times Tray Indicator AppImage
# This script creates a portable AppImage that can run on any Linux system

set -e

APP_NAME="SalahTimesTray"
APP_VERSION="1.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build_tray"
APPDIR="$BUILD_DIR/$APP_NAME.AppDir"

echo "🔨 Building Salah Times Tray AppImage..."

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Create AppDir structure
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/lib"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv "$BUILD_DIR/venv"
source "$BUILD_DIR/venv/bin/activate"

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install PyQt5==5.15.10 requests==2.31.0 beautifulsoup4==4.12.2 pyinstaller

# Create standalone executable
echo "🏗️ Creating standalone executable..."
pyinstaller --onefile \
    --windowed \
    --name="$APP_NAME" \
    --distpath="$APPDIR/usr/bin" \
    --workpath="$BUILD_DIR/work" \
    --specpath="$BUILD_DIR" \
    --add-data="ultra_modern_salah.py:." \
    --hidden-import="PyQt5.QtCore" \
    --hidden-import="PyQt5.QtGui" \
    --hidden-import="PyQt5.QtWidgets" \
    --hidden-import="requests" \
    --hidden-import="bs4" \
    salah_tray_indicator.py

# Create desktop file
cat > "$APPDIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Salah Times Tray
Comment=Islamic prayer times system tray indicator
Exec=$APP_NAME
Icon=salah-times-tray
Categories=Utility;
Terminal=false
StartupNotify=false
X-AppImage-Version=$APP_VERSION
EOF

# Create AppRun script
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash

# AppRun script for Salah Times Tray

HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"

# Set up environment
export QT_QPA_PLATFORM_PLUGIN_PATH="${HERE}/usr/lib/qt5/plugins/platforms"
export QT_PLUGIN_PATH="${HERE}/usr/lib/qt5/plugins"

# Run the application
exec "${HERE}/usr/bin/SalahTimesTray" "$@"
EOF

chmod +x "$APPDIR/AppRun"

# Create icon (simple text-based icon)
cat > "$APPDIR/usr/share/icons/hicolor/256x256/apps/salah-times-tray.svg" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" fill="#2d5a27"/>
  <circle cx="128" cy="80" r="40" fill="#4a7c59"/>
  <rect x="100" y="120" width="56" height="80" fill="#4a7c59"/>
  <rect x="80" y="140" width="16" height="60" fill="#4a7c59"/>
  <rect x="160" y="140" width="16" height="60" fill="#4a7c59"/>
  <text x="128" y="230" text-anchor="middle" fill="white" font-family="Arial" font-size="20" font-weight="bold">SALAH</text>
</svg>
EOF

# Copy icon as PNG (convert from SVG if available)
if command -v convert >/dev/null 2>&1; then
    convert "$APPDIR/usr/share/icons/hicolor/256x256/apps/salah-times-tray.svg" \
            "$APPDIR/usr/share/icons/hicolor/256x256/apps/salah-times-tray.png"
else
    # Create simple PNG icon using ImageMagick alternative or copy SVG
    cp "$APPDIR/usr/share/icons/hicolor/256x256/apps/salah-times-tray.svg" \
       "$APPDIR/salah-times-tray.svg"
fi

# Create main icon link
ln -sf "usr/share/icons/hicolor/256x256/apps/salah-times-tray.svg" "$APPDIR/salah-times-tray.svg"

# Create desktop file link
ln -sf "usr/share/applications/$APP_NAME.desktop" "$APPDIR/$APP_NAME.desktop"

# Download appimagetool if not available
APPIMAGETOOL="$BUILD_DIR/appimagetool"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "📥 Downloading appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
         -O "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
fi

# Build AppImage
echo "🔧 Building AppImage..."
cd "$BUILD_DIR"
ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" "$SCRIPT_DIR/$APP_NAME-$APP_VERSION-x86_64.AppImage"

# Cleanup
deactivate
rm -rf "$BUILD_DIR"

echo "✅ AppImage created: $SCRIPT_DIR/$APP_NAME-$APP_VERSION-x86_64.AppImage"
echo ""
echo "📋 Usage:"
echo "  • Run: ./$APP_NAME-$APP_VERSION-x86_64.AppImage"
echo "  • Install: Move to /usr/local/bin/ or ~/Applications/"
echo "  • Autostart: Run ./setup_system_autostart.sh"
echo ""
echo "🎉 Build complete!"