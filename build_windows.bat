@echo off
echo Building Windows executable...

REM Create virtual environment
python -m venv venv_windows
call venv_windows\Scripts\activate

REM Install dependencies
pip install -r requirements_simple.txt
pip install pyinstaller

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Create Windows executable using spec file
pyinstaller salah_times_windows.spec

if exist "dist\SalahTimes.exe" (
    echo ✅ SUCCESS! Windows executable created:
    dir dist\SalahTimes.exe
    echo.
    echo 📁 Location: %CD%\dist\SalahTimes.exe
    echo 🚀 Ready to run!
) else (
    echo ❌ Build failed - executable not found
)

REM Deactivate virtual environment
deactivate

echo Build complete!
pause