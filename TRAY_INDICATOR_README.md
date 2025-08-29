# Salah Times System Tray Indicator

A lightweight system tray indicator for Islamic prayer times with notifications and Iqama alerts.

## 🎯 Features

- **System Tray Integration**: Runs quietly in the background
- **Prayer Time Notifications**: Desktop notifications at each prayer time
- **Iqama Alerts**: Warning notification 2 minutes before Iqama ends
- **Sound Notifications**: Audio alerts for prayers and Iqama warnings
- **Real-time Updates**: Live countdown in tooltip
- **Multi-language Support**: Arabic, English, French
- **Quick Access**: Right-click menu for easy access to main app

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install PyQt5 requests beautifulsoup4
```

### 2. Run Tray Indicator
```bash
./run_tray.sh
```

### 3. Setup Autostart (Optional)
```bash
./setup_autostart.sh
```

## 📱 Usage

### System Tray Features
- **Left Click**: Show tooltip with next prayer info
- **Right Click**: Open context menu with options:
  - 🕌 Show Salah Times (opens main app)
  - Next Prayer info
  - ↻ Refresh prayer times
  - ⚙️ Settings (opens main app)
  - ❌ Quit

### Notifications
- **Prayer Time**: Desktop notification with sound when prayer time arrives
- **Iqama Warning**: Alert 2 minutes before Iqama time ends
- **Tooltip Updates**: Live countdown to next prayer

### Iqama Timings
- **Fajr**: 20 minutes after Adhan
- **Dhuhr**: 15 minutes after Adhan
- **Asr**: 15 minutes after Adhan
- **Maghrib**: 10 minutes after Adhan
- **Isha**: 15 minutes after Adhan

## 🔧 Configuration

The tray indicator uses the same configuration as the main app:
- **Config File**: `~/.salah_config.json`
- **Settings**: City and language preferences
- **Data Storage**: Prayer times cached locally

## 🎵 Sound Notifications

The app attempts to play system sounds in this order:
1. **PulseAudio**: `paplay` with system sounds
2. **ALSA**: `aplay` with system sounds  
3. **Fallback**: System beep

### Custom Sounds (Optional)
You can replace the sound files or modify the paths in `salah_tray_indicator.py`:
- Prayer notifications: Uses system notification sounds
- Iqama warnings: Uses message notification sounds

## 📁 Files

- `salah_tray_indicator.py` - Main tray indicator application
- `run_tray.sh` - Launcher script
- `salah-tray.desktop` - Desktop entry file
- `setup_autostart.sh` - Autostart configuration script

## 🔄 Autostart Setup

To start the tray indicator automatically on login:

```bash
./setup_autostart.sh
```

This copies the desktop file to `~/.config/autostart/`

To disable autostart:
```bash
rm ~/.config/autostart/salah-tray.desktop
```

## 🛠️ Troubleshooting

### Tray Icon Not Showing
- Ensure your desktop environment supports system tray
- Check if system tray is enabled in your DE settings
- Try restarting the tray indicator

### No Sound Notifications
- Install PulseAudio: `sudo apt install pulseaudio-utils`
- Or install ALSA: `sudo apt install alsa-utils`
- Check system volume settings

### Notifications Not Working
- Ensure notification daemon is running
- Check notification settings in your DE
- Test with: `notify-send "Test" "Message"`

### Permission Issues
```bash
chmod +x run_tray.sh
chmod +x setup_autostart.sh
```

## 🎨 Customization

### Change Notification Timing
Edit `salah_tray_indicator.py` and modify:
- `self.timer.start(30000)` - Check interval (30 seconds)
- Iqama delays in `get_iqama_delay()` method

### Change Icon
Replace the `create_icon()` method in `salah_tray_indicator.py` or use an image file:
```python
self.setIcon(QIcon('/path/to/your/icon.png'))
```

## 🌍 Multi-language Support

The tray indicator automatically uses the language setting from the main app:
- **English**: Default interface
- **Arabic**: Right-to-left prayer names
- **French**: French prayer names and interface

## 📋 System Requirements

- **OS**: Linux (tested on Ubuntu, should work on most distributions)
- **Python**: 3.6+
- **Desktop Environment**: Any DE with system tray support
- **Dependencies**: PyQt5, requests, beautifulsoup4

## 🔗 Integration

The tray indicator integrates seamlessly with the main Salah Times app:
- Shares configuration and prayer data
- Can launch main app from tray menu
- Uses same city and language settings
- Synchronized prayer times and notifications

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Verify system tray support in your DE
4. Check file permissions and paths

---

**Note**: The tray indicator runs independently of the main app and will continue showing notifications even when the main window is closed.