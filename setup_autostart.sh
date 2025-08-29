#!/bin/bash

# Setup autostart for Salah Times Tray Indicator

# Create autostart directory if it doesn't exist
mkdir -p ~/.config/autostart

# Copy desktop file to autostart
cp salah-tray.desktop ~/.config/autostart/

# Make it executable
chmod +x ~/.config/autostart/salah-tray.desktop

echo "Salah Times Tray Indicator has been set to start automatically on login."
echo "To disable autostart, remove: ~/.config/autostart/salah-tray.desktop"