@echo off
echo 🚀 Building Salah Times Windows EXE...

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist venv_windows rmdir /s /q venv_windows

REM Create virtual environment
echo 📦 Setting up virtual environment...
python -m venv venv_windows
call venv_windows\Scripts\activate

REM Install dependencies
echo 📥 Installing dependencies...
pip install --upgrade pip
pip install PyQt5 requests beautifulsoup4 pyinstaller

REM Build executable
echo 🔨 Building executable...
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name SalahTimes ^
    --add-data "app;app" ^
    --hidden-import app.constants ^
    --hidden-import app.database ^
    --hidden-import app.worker ^
    --hidden-import app.dialogs ^
    --hidden-import app.views ^
    --hidden-import app.window ^
    --hidden-import PyQt5.QtPrintSupport ^
    main.py

if exist "dist\SalahTimes.exe" (
    echo.
    echo 🎉 SUCCESS! Windows executable created:
    echo 📄 File: dist\SalahTimes.exe
    for %%A in ("dist\SalahTimes.exe") do echo 📏 Size: %%~zA bytes
    echo.
    echo 🚀 To run: dist\SalahTimes.exe
) else (
    echo ❌ Build failed - executable not found
    exit /b 1
)

call deactivate
echo ✅ Build complete!
pause
