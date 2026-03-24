#!/usr/bin/env python3
"""
Test script to verify single instance functionality
"""
import os
import sys
import time
import subprocess

def test_single_instance():
    print("Testing single instance functionality...")
    
    # Path to the AppImage
    appimage_path = "./SalahTimes-x86_64.AppImage"
    
    if not os.path.exists(appimage_path):
        print("❌ AppImage not found!")
        return False
    
    print("✅ AppImage found")
    
    # Start first instance
    print("🚀 Starting first instance...")
    process1 = subprocess.Popen([appimage_path], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
    
    # Wait a moment for it to start
    time.sleep(3)
    
    # Check if first instance is running
    if process1.poll() is None:
        print("✅ First instance started successfully")
    else:
        print("❌ First instance failed to start")
        return False
    
    # Try to start second instance
    print("🚀 Attempting to start second instance...")
    process2 = subprocess.Popen([appimage_path], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
    
    # Wait a moment
    time.sleep(2)
    
    # Check if second instance was blocked
    if process2.poll() is not None:
        print("✅ Second instance was properly blocked")
        success = True
    else:
        print("❌ Second instance started (this shouldn't happen)")
        success = False
        process2.terminate()
    
    # Clean up first instance
    print("🧹 Cleaning up...")
    process1.terminate()
    process1.wait()
    
    return success

if __name__ == "__main__":
    if test_single_instance():
        print("\n🎉 Single instance test PASSED!")
    else:
        print("\n❌ Single instance test FAILED!")
        sys.exit(1)