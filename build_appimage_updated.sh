#!/bin/bash

# Build AppImage for Salah Times with Display Features
echo "🚀 Building Salah Times AppImage..."

# Clean previous builds
rm -rf build/ dist/ venv_appimage/ SalahTimes.AppDir/ *.AppImage

# Create virtual environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv_appimage
source venv_appimage/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install PyQt5 requests beautifulsoup4 pyinstaller

# Create PyInstaller spec file
echo "📝 Creating PyInstaller spec..."
cat > salah_times_updated.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ultra_modern_salah.py'],
    pathex=[],
    binaries=[],
    datas=[('display_features_fixed.py', '.')],
    hiddenimports=['PyQt5.QtPrintSupport'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SalahTimes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Build executable
echo "🔨 Building executable..."
pyinstaller salah_times_updated.spec

# Check if build was successful
if [ ! -f "dist/SalahTimes" ]; then
    echo "❌ Build failed - executable not found"
    exit 1
fi

echo "✅ Executable built successfully"

# Download AppImage tools if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "📥 Downloading AppImage tools..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Create AppDir structure
echo "📁 Creating AppDir structure..."
mkdir -p SalahTimes.AppDir/usr/bin
mkdir -p SalahTimes.AppDir/usr/share/applications
mkdir -p SalahTimes.AppDir/usr/share/icons/hicolor/256x256/apps

# Copy executable
cp dist/SalahTimes SalahTimes.AppDir/usr/bin/
chmod +x SalahTimes.AppDir/usr/bin/SalahTimes

# Create desktop file
echo "📋 Creating desktop file..."
cat > SalahTimes.AppDir/salah-times.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Salah Times
Comment=Modern Prayer Times App with Calendar Views
Exec=SalahTimes
Icon=salah-times
Categories=Utility;Office;
Keywords=prayer;islam;salah;times;calendar;
StartupNotify=true
EOF

# Copy desktop file
cp SalahTimes.AppDir/salah-times.desktop SalahTimes.AppDir/usr/share/applications/

# Create AppRun script
echo "🏃 Creating AppRun..."
cat > SalahTimes.AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/SalahTimes" "$@"
EOF
chmod +x SalahTimes.AppDir/AppRun

# Create icon
echo "🎨 Creating icon..."
cat > SalahTimes.AppDir/salah-times.svg << 'EOF'
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4a7c59;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2d5a27;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="256" height="256" fill="url(#bg)" rx="32"/>
  <text x="128" y="160" font-family="Arial, sans-serif" font-size="120" fill="white" text-anchor="middle">🕌</text>
  <text x="128" y="220" font-family="Arial, sans-serif" font-size="24" fill="white" text-anchor="middle" opacity="0.9">Prayer Times</text>
</svg>
EOF

# Copy icon
cp SalahTimes.AppDir/salah-times.svg SalahTimes.AppDir/usr/share/icons/hicolor/256x256/apps/
cp SalahTimes.AppDir/salah-times.svg SalahTimes.AppDir/

# Build AppImage
echo "📦 Building AppImage..."
./appimagetool-x86_64.AppImage SalahTimes.AppDir SalahTimes-x86_64.AppImage

# Check if AppImage was created
if [ -f "SalahTimes-x86_64.AppImage" ]; then
    echo "🎉 AppImage created successfully!"
    echo "📄 File: SalahTimes-x86_64.AppImage"
    echo "📏 Size: $(du -h SalahTimes-x86_64.AppImage | cut -f1)"
    echo ""
    echo "🚀 To run: ./SalahTimes-x86_64.AppImage"
    echo "📦 To install: chmod +x SalahTimes-x86_64.AppImage && ./SalahTimes-x86_64.AppImage"
    echo ""
    echo "✨ Features included:"
    echo "   📅 Monthly Calendar View"
    echo "   📋 Weekly Schedule View"
    echo "   🌍 Multiple Timezone View"
    echo "   🕌 43 Moroccan Cities"
    echo "   🌐 3 Languages (EN/AR/FR)"
else
    echo "❌ AppImage creation failed"
    exit 1
fi

# Cleanup
echo "🧹 Cleaning up..."
deactivate
rm -rf venv_appimage/ build/ dist/ SalahTimes.AppDir/

echo "✅ Build complete!"