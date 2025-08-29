#!/usr/bin/env python3
"""
Test script for Salah Times Tray Indicator
This script tests the basic functionality without requiring a full GUI environment
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test PyQt5
        from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
        from PyQt5.QtCore import QTimer
        from PyQt5.QtGui import QIcon
        print("✅ PyQt5 imported successfully")
        
        # Test main app components
        from ultra_modern_salah import PrayerTimeWorker, CITIES, TRANSLATIONS
        print("✅ Main app components imported successfully")
        
        # Test tray indicator
        from salah_tray_indicator import SalahTrayIndicator, SalahTrayApp
        print("✅ Tray indicator imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_data_structures():
    """Test if data structures are properly configured"""
    try:
        print("\nTesting data structures...")
        
        from ultra_modern_salah import CITIES, TRANSLATIONS
        
        # Test cities
        print(f"✅ Cities available: {len(CITIES)}")
        print(f"   Sample cities: {list(CITIES.keys())[:5]}")
        
        # Test translations
        print(f"✅ Languages available: {list(TRANSLATIONS.keys())}")
        
        # Test prayer names in each language
        for lang in TRANSLATIONS.keys():
            prayers = TRANSLATIONS[lang]['prayers']
            print(f"   {lang}: {len(prayers)} prayers")
        
        return True
        
    except Exception as e:
        print(f"❌ Data structure error: {e}")
        return False

def test_system_tray_support():
    """Test if system tray is supported"""
    try:
        print("\nTesting system tray support...")
        
        # Create minimal QApplication
        app = QApplication([])
        
        # Check system tray availability
        if QSystemTrayIcon.isSystemTrayAvailable():
            print("✅ System tray is available")
            return True
        else:
            print("❌ System tray is not available on this system")
            return False
            
    except Exception as e:
        print(f"❌ System tray test error: {e}")
        return False

def test_config_file():
    """Test configuration file handling"""
    try:
        print("\nTesting configuration...")
        
        import json
        config_file = os.path.expanduser('~/.salah_config.json')
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"✅ Config file exists: {config}")
        else:
            print("ℹ️  Config file doesn't exist (will be created on first run)")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Salah Times Tray Indicator")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_data_structures,
        test_system_tray_support,
        test_config_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Tray indicator should work correctly.")
        print("\n💡 To run the tray indicator:")
        print("   ./run_tray.sh")
        print("\n💡 To set up autostart:")
        print("   ./setup_autostart.sh")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        
        if passed >= 2:  # If basic imports work
            print("\n💡 You can still try running the tray indicator:")
            print("   ./run_tray.sh")

if __name__ == '__main__':
    main()