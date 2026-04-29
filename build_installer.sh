#!/bin/bash
set -e

echo "🚀 Building Salah Times Windows Installer..."

BASEDIR="$(pwd)"
WINEPATH=$(winepath -w "$BASEDIR" 2>/dev/null | tr -d '\r\n')
NSIS="$HOME/.wine/drive_c/Program Files (x86)/NSIS/makensis.exe"

# Clean
rm -rf build/ dist/

# Install Wine Python deps if needed
echo "📥 Checking Wine Python dependencies..."
wine pip install PyQt5 requests beautifulsoup4 pyinstaller pillow -q 2>/dev/null

# Generate icon
echo "🎨 Generating icon..."
mkdir -p installer
env/bin/python - << 'PYEOF'
import os, sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QBrush, QPen, QLinearGradient
from PyQt5.QtCore import Qt, QRect
app = QApplication(sys.argv)
px = QPixmap(256, 256)
px.fill(Qt.transparent)
p = QPainter(px)
p.setRenderHint(QPainter.Antialiasing)
grad = QLinearGradient(0, 0, 256, 256)
grad.setColorAt(0, QColor('#4a7c59'))
grad.setColorAt(1, QColor('#2d5a27'))
p.setBrush(QBrush(grad))
p.setPen(Qt.NoPen)
p.drawRoundedRect(0, 0, 256, 256, 30, 30)
p.setPen(QPen(QColor('white')))
p.setFont(QFont('Arial', 140))
p.drawText(QRect(0, 0, 256, 256), Qt.AlignCenter, '🕌')
p.end()
px.save('installer/salah_times.png')
PYEOF

env/bin/python -c "
from PIL import Image
img = Image.open('installer/salah_times.png').convert('RGBA')
img.save('installer/salah_times.ico', format='ICO', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
print('  ✓ Icon generated')
"

# Build EXE with Wine PyInstaller
echo "🔨 Building SalahTimes.exe..."
wine pyinstaller --noconfirm \
    --onefile \
    --windowed \
    --name SalahTimes \
    --icon "installer/salah_times.ico" \
    --add-data "app;app" \
    --hidden-import app.constants \
    --hidden-import app.database \
    --hidden-import app.worker \
    --hidden-import app.dialogs \
    --hidden-import app.views \
    --hidden-import app.window \
    --hidden-import PyQt5.QtPrintSupport \
    main.py 2>&1 | grep -E "Building EXE|completed successfully|ERROR"

if [ ! -f "dist/SalahTimes.exe" ]; then
    echo "❌ EXE build failed"
    exit 1
fi
echo "  ✓ SalahTimes.exe built ($(du -h dist/SalahTimes.exe | cut -f1))"

# Build installer with NSIS
echo "📦 Building installer..."
wine "$NSIS" "/DBASEDIR=$WINEPATH" installer/installer.nsi 2>&1 | grep -v "fixme\|wineusb\|winebth\|autostart" | grep -E "Output|Error|Total size"

if [ -f "SalahTimes-Setup.exe" ]; then
    echo ""
    echo "🎉 Done!"
    echo "📄 SalahTimes-Setup.exe ($(du -h SalahTimes-Setup.exe | cut -f1))"
    echo ""
    echo "The installer will:"
    echo "  • Install to C:\\Program Files\\Salah Times"
    echo "  • Require admin rights"
    echo "  • Create Start Menu + Desktop shortcuts with icon"
    echo "  • Register in Add/Remove Programs"
else
    echo "❌ Installer build failed"
    exit 1
fi

rm -rf build/ dist/
echo "✅ Build complete!"
