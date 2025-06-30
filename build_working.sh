#!/bin/bash

# Working build script without lxml
echo "Building executable without lxml..."

# Create virtual environment
python -m venv venv_simple
source venv_simple/bin/activate

# Install simplified dependencies
pip install -r requirements_simple.txt
pip install pyinstaller

# Clean previous builds
rm -rf build/ dist/

# Create executable
pyinstaller salah_times.spec

echo "Executable created: dist/SalahTimes"
echo "Testing executable..."

# Test the executable
if [ -f "dist/SalahTimes" ]; then
    chmod +x dist/SalahTimes
    echo "Executable is ready!"
    echo "Run with: ./dist/SalahTimes"
else
    echo "Build failed - executable not found"
fi

# Deactivate virtual environment
deactivate