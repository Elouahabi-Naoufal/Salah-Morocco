#!/bin/bash

echo "🚀 Building Salah Times AppImage..."

rm -rf build/ dist/ venv_appimage/ SalahTimes.AppDir/

echo "📦 Setting up virtual environment..."
python3 -m venv venv_appimage
source venv_appimage/bin/activate

echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install PyQt5 requests beautifulsoup4 pyinstaller PyGObject pycairo

echo "📝 Creating PyInstaller spec..."
cat > salah_times_updated.spec << 'SPECEOF'
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('app', 'app')],
    hiddenimports=[
        'PyQt5.QtPrintSupport',
        'gi',
        'gi.repository.AyatanaAppIndicator3',
        'gi.repository.Gtk',
        'gi.repository.GLib',
        'gi.repository.GObject',
        'app.constants',
        'app.database',
        'app.worker',
        'app.dialogs',
        'app.views',
        'app.window',
        'app.tray',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SalahTimes',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)
SPECEOF

echo "🔨 Building executable..."
pyinstaller salah_times_updated.spec

if [ ! -f "dist/SalahTimes" ]; then
    echo "❌ Build failed - executable not found"
    exit 1
fi
echo "✅ Executable built successfully"

if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "📥 Downloading AppImage tools..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

echo "📁 Creating AppDir structure..."
mkdir -p SalahTimes.AppDir/usr/bin
mkdir -p SalahTimes.AppDir/usr/share/applications
mkdir -p SalahTimes.AppDir/usr/share/icons/hicolor/256x256/apps
mkdir -p SalahTimes.AppDir/usr/lib/girepository-1.0
mkdir -p SalahTimes.AppDir/usr/lib

echo "📦 Bundling GObject typelibs..."
for typelib in AyatanaAppIndicator3-0.1 Gtk-3.0 GLib-2.0 GObject-2.0 Gio-2.0 GLibUnix-2.0; do
    src="/usr/lib/girepository-1.0/${typelib}.typelib"
    if [ -f "$src" ]; then
        cp "$src" SalahTimes.AppDir/usr/lib/girepository-1.0/
        echo "  ✓ $typelib"
    else
        echo "  ⚠ Missing: $typelib"
    fi
done

echo "📦 Bundling libayatana-appindicator3..."
cp -P /usr/lib/libayatana-appindicator3.so* SalahTimes.AppDir/usr/lib/ 2>/dev/null \
    && echo "  ✓ libayatana-appindicator3" \
    || echo "  ⚠ libayatana-appindicator3 not found"

cp dist/SalahTimes SalahTimes.AppDir/usr/bin/
chmod +x SalahTimes.AppDir/usr/bin/SalahTimes

echo "📋 Creating desktop file..."
cat > SalahTimes.AppDir/salah-times.desktop << 'DESKEOF'
[Desktop Entry]
Type=Application
Name=Salah Times
Comment=Modern Prayer Times App
Exec=SalahTimes
Icon=salah-times
Categories=Utility;
Keywords=prayer;islam;salah;times;
StartupNotify=true
DESKEOF

cp SalahTimes.AppDir/salah-times.desktop SalahTimes.AppDir/usr/share/applications/

echo "🏃 Creating AppRun..."
cat > SalahTimes.AppDir/AppRun << 'RUNEOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export GI_TYPELIB_PATH="${HERE}/usr/lib/girepository-1.0:/usr/lib/girepository-1.0:/usr/lib/x86_64-linux-gnu/girepository-1.0"
export GSETTINGS_BACKEND=memory
export GSETTINGS_SCHEMA_DIR=/usr/share/glib-2.0/schemas
export GTK_MODULES=''
exec "${HERE}/usr/bin/SalahTimes" "$@"
RUNEOF
chmod +x SalahTimes.AppDir/AppRun

echo "🎨 Creating icon..."
cat > SalahTimes.AppDir/salah-times.svg << 'SVGEOF'
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
SVGEOF

cp SalahTimes.AppDir/salah-times.svg SalahTimes.AppDir/usr/share/icons/hicolor/256x256/apps/

echo "🧹 Removing bundled glib schemas..."
rm -rf SalahTimes.AppDir/usr/share/glib-2.0/schemas/
rm -rf SalahTimes.AppDir/usr/lib/python*/site-packages/gi/schemas/ 2>/dev/null || true

echo "📦 Building AppImage..."
./appimagetool-x86_64.AppImage SalahTimes.AppDir SalahTimes-x86_64.AppImage

if [ -f "SalahTimes-x86_64.AppImage" ]; then
    echo "🎉 AppImage created successfully!"
    echo "📏 Size: $(du -h SalahTimes-x86_64.AppImage | cut -f1)"
else
    echo "❌ AppImage creation failed"
    exit 1
fi

echo "🧹 Cleaning up..."
deactivate
rm -rf venv_appimage/ build/ dist/ SalahTimes.AppDir/

echo "✅ Build complete!"
