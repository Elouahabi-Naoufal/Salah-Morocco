#!/bin/bash

# Salah Times Tray Indicator Launcher
# This script starts the system tray indicator for prayer times

cd "$(dirname "$0")"

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python3 is required but not installed."
    exit 1
fi

# Check if required packages are installed
python3 -c "import PyQt5" 2>/dev/null || {
    echo "PyQt5 is required. Install with: pip3 install PyQt5"
    exit 1
}

# Start the tray indicator
echo "Starting Salah Times Tray Indicator..."
python3 salah_tray_indicator.py &

# Store PID for later use
echo $! > /tmp/salah_tray.pid
echo "Salah Times Tray Indicator started (PID: $!)"
echo "To stop: kill \$(cat /tmp/salah_tray.pid)"