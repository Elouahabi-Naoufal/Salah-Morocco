# Salah Times - Multi-Platform Prayer Times App

A modern, multilingual prayer times application supporting Arabic, French, and English languages.

## 🎯 Features

- 🕌 Real-time prayer times for 43 Moroccan cities
- 🌍 Multilingual support (Arabic, English, French)
- 📅 Hijri and Gregorian dates
- ⏰ Iqama countdown timer
- 🎨 Modern, elegant UI design
- 🔄 Auto-refresh functionality

## 📱 App Preview

### **Desktop Interface (PyQt5)**
```
┌─────────────────────────────────────┐
│  🕌 Salah Times - Tangier          │
│  Tangier, Morocco                   │
│                    ⚙️               │
├─────────────────────────────────────┤
│  15 Rabi al-Awwal 1446 AH          │
│  Monday, December 30, 2024          │
├─────────────────────────────────────┤
│  📅 Date      30/12                 │
│  🌌 Fajr      06:42                 │
│  🌞 Sunrise   08:12                 │
│  🔆 Dhuhr     13:25                 │
│  🌅 Asr       15:58                 │
│  🌇 Maghrib   18:35                 │
│  🌃 Isha      20:05                 │
├─────────────────────────────────────┤
│         NEXT PRAYER                 │
│           Dhuhr                     │
│           13:25                     │
│         02:15:30                    │
│  Time before Iqama: 00:12:45       │
├─────────────────────────────────────┤
│         ↻ Refresh                   │
└─────────────────────────────────────┘
```

### **Language Support**
- **English**: Modern clean interface
- **Arabic**: Right-to-left layout with Arabic text
- **French**: Simplified French without accents

### **Key UI Elements**
- **Header**: App title, location, settings button
- **Date Card**: Hijri and Gregorian dates
- **Prayer Times**: Icons, names, and times
- **Next Prayer**: Countdown with Iqama timer
- **Controls**: Language/city selection, refresh

## 📱 Supported Platforms

- **Linux** (AppImage)
- **Windows** (Executable)
- **Android** (APK)
- **iOS** (via Kivy-iOS)

## 📁 File Utility Explanation

### **🎯 Core Applications:**

**`ultra_modern_salah.py`** (48KB)
- **Main desktop application** using PyQt5
- **Features**: 43 cities, 3 languages, prayer times, Hijri calendar, Iqama timer
- **Platform**: Linux, Windows desktop
- **UI**: Modern GUI with cards, settings, countdown

**`main.py`** (9KB) 
- **Mobile version** using Kivy framework
- **Features**: Touch-friendly interface, 8 major cities, 3 languages
- **Platform**: Android, iOS
- **UI**: Mobile-optimized layout

### **⚙️ Build Configurations:**

**`buildozer.spec`** (466 bytes)
- **Android build settings** for Kivy app
- **Defines**: App name, package, permissions, Android API levels
- **Used by**: `build_android_working.sh`

**`salah_times_windows.spec`** (1KB)
- **Windows build settings** for PyInstaller
- **Defines**: Dependencies, executable settings, icon
- **Used by**: `build_windows.bat`

**`requirements_simple.txt`** (54 bytes)
- **Python dependencies** list
- **Contains**: PyQt5, requests, beautifulsoup4 (no lxml issues)
- **Used by**: All build scripts

### **🛠️ Build Scripts:**

**`build_appimage.sh`** (2KB)
- **Creates Linux AppImage** (portable app)
- **Process**: Virtual env → PyInstaller → AppImage packaging
- **Output**: `SalahTimes-x86_64.AppImage`

**`build_windows.bat`** (738 bytes)
- **Creates Windows EXE** file
- **Process**: Virtual env → PyInstaller → Standalone EXE
- **Output**: `dist\SalahTimes.exe`

**`build_android_working.sh`** (1KB)
- **Creates Android APK** file
- **Process**: Buildozer → Android SDK/NDK → APK
- **Output**: `bin/salahtimes-*.apk`

**`build_working.sh`** (703 bytes)
- **Creates simple Linux executable**
- **Process**: PyInstaller → Binary
- **Output**: `dist/SalahTimes`

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

## 🚀 Building Instructions

### Linux AppImage
```bash
./build_appimage.sh
```

### Windows Executable
```batch
build_windows.bat
```

### Android APK
```bash
./build_android_working.sh
```

## 🎯 Usage Summary
- **Desktop**: Use `ultra_modern_salah.py` + build scripts
- **Mobile**: Use `main.py` + `buildozer.spec`
- **Linux**: Run `build_appimage.sh`
- **Windows**: Run `build_windows.bat`
- **Android**: Run `build_android_working.sh`

## 🏙️ Cities Supported

All major Moroccan cities including:
- Tangier, Casablanca, Rabat, Marrakech, Fes
- Agadir, Meknes, Oujda, Kenitra, Tetouan
- And 33 more cities across Morocco

## 📄 License

MIT License - Feel free to use and modify

Each file has a specific purpose in creating multi-platform Salah Times applications! 🕌