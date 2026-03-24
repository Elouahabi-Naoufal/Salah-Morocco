# AppImage Multiple Instance Fix

## Problem
The AppImage was launching two instances of the application and the tray icon wasn't working properly.

## Root Cause
1. **Separate Tray Process**: The build was including both the main application (`ultra_modern_salah.py`) and a separate tray indicator (`salah_tray_indicator.py`), causing two processes to run.
2. **No Single Instance Check**: There was no mechanism to prevent multiple instances from running simultaneously.

## Fixes Applied

### 1. Removed Separate Tray Indicator from Build
**File**: `build_appimage_updated.sh`
```bash
# BEFORE
datas=[('display_features_fixed.py', '.'), ('salah_tray_indicator.py', '.')],

# AFTER  
datas=[('display_features_fixed.py', '.')],
```

### 2. Added Single Instance Lock Mechanism
**File**: `ultra_modern_salah.py`
- Added PID-based lock file system in `~/.salah_times/app.lock`
- Checks if another instance is running before starting
- Properly cleans up lock file on exit

### 3. Improved Tray Icon Management
**File**: `ultra_modern_salah.py`
- Added prevention of multiple tray icon creation
- Improved cleanup on application quit
- Added proper tray icon activation handling
- Fixed window minimize/restore behavior

### 4. Enhanced Application Lifecycle
- Added proper signal handling
- Improved cleanup on quit
- Better error handling for tray operations

## Key Changes Made

### Single Instance Check
```python
# Check if another instance is already running
lock_file = os.path.join(os.path.expanduser('~'), '.salah_times', 'app.lock')

if os.path.exists(lock_file):
    try:
        with open(lock_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process is still running
        os.kill(pid, 0)  # Signal 0 just checks if process exists
        print("Another instance is already running")
        sys.exit(0)
    except OSError:
        # Process doesn't exist, remove stale lock file
        os.remove(lock_file)
```

### Tray Icon Prevention
```python
def start_tray_indicator(self):
    # Prevent multiple tray icons
    if self.tray_icon is not None:
        print("Debug: Tray icon already exists, skipping creation")
        return
    
    # Create tray icon...
```

### Proper Cleanup
```python
def cleanup_and_quit(self):
    """Clean up resources and quit"""
    if self.tray_icon:
        self.tray_icon.hide()
        self.tray_icon = None
    self.save_geometry()
    QApplication.quit()
```

## Result
- ✅ Single instance enforcement
- ✅ Proper tray icon functionality  
- ✅ No duplicate processes
- ✅ Clean application lifecycle
- ✅ Proper window minimize/restore

## Testing
Run the test script to verify:
```bash
python3 test_single_instance.py
```

## AppImage Size
- **Before**: ~61MB
- **After**: ~61MB (same size, just cleaner architecture)

## Files Modified
1. `ultra_modern_salah.py` - Main application fixes
2. `build_appimage_updated.sh` - Build configuration fixes
3. `test_single_instance.py` - Testing script (new)
4. `APPIMAGE_FIXES.md` - This documentation (new)