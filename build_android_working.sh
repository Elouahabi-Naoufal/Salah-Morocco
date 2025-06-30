#!/bin/bash

# Working Android build script
echo "🤖 Building Android APK..."

# Clean previous attempts
rm -rf venv_android .buildozer bin/

# Create fresh virtual environment
python -m venv venv_android
source venv_android/bin/activate

# Install requirements with setuptools first
pip install setuptools wheel
pip install -r android_requirements.txt

# Set environment variables
export JAVA_HOME=/usr/lib/jvm/java-24-openjdk
export PATH=$JAVA_HOME/bin:$PATH
export PYTHONPATH=$PWD:$PYTHONPATH

echo "📱 Starting buildozer..."
echo "⏳ This will take several minutes (downloading Android SDK/NDK)..."

# Build APK
buildozer android debug

# Check result
if [ -d "bin" ] && [ -f bin/*.apk ]; then
    echo "✅ SUCCESS! Android APK created:"
    ls -la bin/*.apk
    echo ""
    echo "📲 To install on device:"
    echo "   adb install bin/*.apk"
    echo ""
    echo "📁 APK location: $(pwd)/bin/"
else
    echo "❌ Build failed - checking logs..."
    if [ -f ".buildozer/android/platform/build-*/build.log" ]; then
        echo "Last few lines of build log:"
        tail -20 .buildozer/android/platform/build-*/build.log
    fi
fi

deactivate