# Salah Times v2.0 - Multi-Platform Prayer Times App

A modern, multilingual prayer times application with advanced calendar and scheduling features.

## Features

### Core Features
- Real-time prayer times for 43 Moroccan cities
- Multilingual support (Arabic, English, French)
- Hijri and Gregorian dates
- Iqama countdown timer
- Modern, elegant UI design
- Auto-refresh functionality
- System tray integration with notifications

### NEW in v2.0: Display Features
- **Monthly Calendar View** - Full month prayer times in calendar format
- **Weekly Schedule View** - 7-day prayer schedule with navigation
- **Multiple Timezone View** - Compare prayer times across cities
- **Enhanced Menu System** - Easy access via View menu
- **Export Functionality** - PDF export for monthly calendars

## App Interface

### Main Application
- Modern gradient design with Islamic green theme
- Prayer times grid with current prayer highlighting
- Real-time countdown to next prayer
- Iqama timing with customizable delays
- System tray integration

### Display Views (NEW in v2.0)

#### Monthly Calendar View
- Full month prayer times in calendar grid
- Month navigation (Previous/Next)
- Today highlighting and weekend highlighting
- Export to PDF functionality

#### Weekly Schedule View
- 7-day prayer schedule table
- Week navigation controls
- Current day highlighting
- Localized day names

#### Multiple Timezone View
- Multi-city prayer times comparison
- City coordinates display
- Real-time local time
- Dynamic city addition/removal

### Language Support
- **English**: Complete interface
- **Arabic**: Full RTL support with Arabic text
- **French**: French interface without accents

## Supported Platforms

- **Linux** (AppImage) - v2.0 Ready
- **Windows** (Executable) - v1.0 Compatible
- **Android** (APK) - v1.0 Compatible
- **iOS** (via Kivy-iOS) - v1.0 Compatible

## File Structure

### Core Applications

**`ultra_modern_salah.py`**
- Main desktop application using PyQt5
- Features: 43 cities, 3 languages, prayer times, Hijri calendar, Iqama timer
- NEW: Monthly calendar, weekly schedule, timezone comparison views
- Platform: Linux, Windows desktop
- UI: Modern GUI with gradient design and display features

**`display_features_fixed.py`**
- NEW: Display feature dialogs (Monthly, Weekly, Timezone views)
- Professional table layouts with navigation
- Export functionality and multi-city comparison
- Full integration with main application

**`main.py`**
- Mobile version using Kivy framework
- Features: Touch-friendly interface, 8 major cities, 3 languages
- Platform: Android, iOS
- UI: Mobile-optimized layout

### Build Configurations

**`buildozer.spec`**
- Android build settings for Kivy app
- Defines: App name, package, permissions, Android API levels
- Used by: `build_android_working.sh`

**`salah_times_updated.spec`**
- NEW: Updated PyInstaller spec for v2.0 with display features
- Includes: display_features_fixed.py and PyQt5.QtPrintSupport
- Used by: `build_appimage_updated.sh`

**`requirements_simple.txt`**
- Python dependencies list
- Contains: PyQt5, requests, beautifulsoup4
- Used by: All build scripts

### Build Scripts

**`build_appimage_updated.sh`** (NEW)
- Creates Linux AppImage with v2.0 features
- Process: Virtual env → PyInstaller → AppImage packaging
- Output: `SalahTimes-x86_64.AppImage` (61MB)
- Includes: All display features and dependencies

**`build_windows.bat`**
- Creates Windows EXE file
- Process: Virtual env → PyInstaller → Standalone EXE
- Output: `dist\SalahTimes.exe`

**`build_android_working.sh`**
- Creates Android APK file
- Process: Buildozer → Android SDK/NDK → APK
- Output: `bin/salahtimes-*.apk`

**`build_appimage.sh`** (Legacy)
- Original Linux build script for v1.0
- Use `build_appimage_updated.sh` for v2.0 features

### **📚 Documentation:**

**`README.md`** (1.9KB)
- **Main project documentation**
- **Contains**: Features, supported platforms, build instructions

**`BUILD_INSTRUCTIONS.md`** (1.8KB)
- **General build guide**
- **Contains**: Quick start, tested platforms, distribution info

**`ANDROID_BUILD_GUIDE.md`** (1.9KB)
- **Android-specific instructions**
- **Contains**: Prerequisites, Java setup, APK creation

**`WINDOWS_BUILD_GUIDE.md`** (2.2KB)
- **Windows-specific instructions**
- **Contains**: Build process, distribution, file structure

## Building Instructions

### Linux AppImage (v2.0 with Display Features)
```bash
bash build_appimage_updated.sh
```

### Windows Executable
```batch
build_windows.bat
```

### Android APK
```bash
./build_android_working.sh
```

## Quick Start

### Linux (Recommended)
1. Download `SalahTimes-x86_64.AppImage`
2. Make executable: `chmod +x SalahTimes-x86_64.AppImage`
3. Run: `./SalahTimes-x86_64.AppImage`
4. Access new features via View menu

### From Source
1. Clone repository
2. Install dependencies: `pip install PyQt5 requests beautifulsoup4`
3. Run: `python ultra_modern_salah.py`

## Usage Summary
- **Desktop v2.0**: Use `ultra_modern_salah.py` with display features
- **Mobile**: Use `main.py` + `buildozer.spec`
- **Linux v2.0**: Run `build_appimage_updated.sh`
- **Windows**: Run `build_windows.bat`
- **Android**: Run `build_android_working.sh`

## Cities Supported

43 Moroccan cities including:
- Major cities: Tangier, Casablanca, Rabat, Marrakech, Fes, Agadir
- Regional centers: Meknes, Oujda, Kenitra, Tetouan, Safi, Mohammedia
- All cities with precise coordinates for accurate prayer time calculations
- Full support in timezone comparison view

## Version History

### v2.0 (Current)
- Added Monthly Calendar View
- Added Weekly Schedule View
- Added Multiple Timezone View
- Enhanced UI with modern design
- Professional AppImage distribution

### v1.0
- Basic prayer times display
- 43 Moroccan cities
- 3 language support
- System tray integration

## License

MIT License - Feel free to use and modify

## Contributing

Contributions welcome! Please ensure new features maintain compatibility with existing functionality and support all three languages (Arabic, English, French).