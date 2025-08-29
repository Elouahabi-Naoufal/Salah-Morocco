#!/bin/bash

# Quick start script for Salah Times Tray
# This script runs the tray indicator directly without building AppImage

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"
python3 salah_tray_indicator.py &
echo $! > /tmp/salah_tray.pid