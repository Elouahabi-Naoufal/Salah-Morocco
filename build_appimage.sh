#!/bin/bash

# Build AppImage for Linux
echo "Building AppImage for Linux..."

# Create virtual environment and install dependencies
python -m venv venv_appimage
source venv_appimage/bin/activate
pip install -r requirements_simple.txt
pip install pyinstaller

# Clean and create executable
rm -rf build/ dist/
pyinstaller salah_times.spec

# Download AppImage tools
wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Create AppDir structure
mkdir -p SalahTimes.AppDir/usr/bin
mkdir -p SalahTimes.AppDir/usr/share/applications
mkdir -p SalahTimes.AppDir/usr/share/icons/hicolor/256x256/apps

# Copy executable and ensure it works
cp dist/SalahTimes SalahTimes.AppDir/usr/bin/
chmod +x SalahTimes.AppDir/usr/bin/SalahTimes

# Test executable before packaging
echo "Testing executable..."
if ! ./SalahTimes.AppDir/usr/bin/SalahTimes --help 2>/dev/null; then
    echo "Warning: Executable may have issues"
fi

# Create desktop file
cat > SalahTimes.AppDir/salah-times.desktop << EOF
[Desktop Entry]
Type=Application
Name=Salah Times
Comment=Modern Prayer Times App
Exec=SalahTimes
Icon=salah-times
Categories=Utility;
EOF

# Copy desktop file
cp SalahTimes.AppDir/salah-times.desktop SalahTimes.AppDir/usr/share/applications/

# Create AppRun
cat > SalahTimes.AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/SalahTimes" "$@"
EOF
chmod +x SalahTimes.AppDir/AppRun

# Create icon (simple text-based icon)
cat > SalahTimes.AppDir/salah-times.svg << 'EOF'
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" fill="#2d5a27"/>
  <text x="128" y="140" font-family="Arial" font-size="80" fill="white" text-anchor="middle">🕌</text>
</svg>
EOF

cp SalahTimes.AppDir/salah-times.svg SalahTimes.AppDir/usr/share/icons/hicolor/256x256/apps/

# Build AppImage
./appimagetool-x86_64.AppImage SalahTimes.AppDir SalahTimes-x86_64.AppImage

echo "AppImage created: SalahTimes-x86_64.AppImage"