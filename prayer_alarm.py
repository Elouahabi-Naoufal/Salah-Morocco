#!/usr/bin/env python3
import sys
import os
import json
import subprocess
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class PrayerAlarmDialog(QDialog):
    def __init__(self, prayer_name, prayer_time, language='en', parent=None):
        super().__init__(parent)
        self.prayer_name = prayer_name
        self.prayer_time = prayer_time
        self.language = language
        self.config_dir = os.path.join(os.path.expanduser('~'), '.salah_times', 'config')
        self.notifications_config = self.load_notification_settings()
        self.snooze_duration = self.notifications_config.get('snooze_duration', 5)
        self.sound_enabled = self.notifications_config.get('sound_enabled', True)
        
        self.init_ui()
        self.play_alarm_sound()
        
        # Auto-close timer (30 seconds)
        self.auto_close_timer = QTimer()
        self.auto_close_timer.timeout.connect(self.auto_dismiss)
        self.auto_close_timer.start(30000)
        
        # Flash timer for attention
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self.flash_window)
        self.flash_timer.start(500)
        self.flash_state = False
    
    def init_ui(self):
        self.setWindowTitle(f"🕌 {self.prayer_name} Prayer Time")
        self.setFixedSize(400, 300)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        
        # Center on screen
        screen = QDesktopWidget().screenGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)
        
        self.setStyleSheet(self.get_alarm_stylesheet())
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Prayer icon
        icon_label = QLabel(self.get_prayer_icon())
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 64px;")
        layout.addWidget(icon_label)
        
        # Prayer name
        prayer_label = QLabel(f"🕌 {self.prayer_name} Prayer Time")
        prayer_label.setProperty("class", "alarm_title")
        prayer_label.setAlignment(Qt.AlignCenter)
        prayer_label.setWordWrap(True)
        layout.addWidget(prayer_label)
        
        # Time
        time_label = QLabel(self.prayer_time)
        time_label.setProperty("class", "alarm_time")
        time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(time_label)
        
        # Message
        message = QLabel("It's time for prayer")
        message.setProperty("class", "alarm_message")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        layout.addWidget(message)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Snooze button
        snooze_btn = QPushButton(f"😴 Snooze ({self.snooze_duration} min)")
        snooze_btn.setProperty("class", "snooze_button")
        snooze_btn.clicked.connect(self.snooze_alarm)
        snooze_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(snooze_btn)
        
        # Stop button
        stop_btn = QPushButton("⏹️ Stop")
        stop_btn.setProperty("class", "stop_button")
        stop_btn.clicked.connect(self.stop_alarm)
        stop_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(stop_btn)
        
        layout.addLayout(button_layout)
    
    def get_alarm_stylesheet(self):
        return """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d5a27, stop:1 #4a7c59);
                border: 3px solid #FFD700;
                border-radius: 15px;
            }
            
            .alarm_title {
                color: white;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            .alarm_time {
                color: #FFD700;
                font-size: 32px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            .alarm_message {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                font-weight: 500;
            }
            
            .snooze_button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFA500, stop:1 #FF8C00);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }
            
            .snooze_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFB84D, stop:1 #FFA500);
            }
            
            .stop_button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #DC143C, stop:1 #B22222);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }
            
            .stop_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FF6B6B, stop:1 #DC143C);
            }
        """
    
    def get_prayer_icon(self):
        icons = {
            'Fajr': '🌌',
            'Dohr': '🔆', 
            'Asr': '🌅',
            'Maghreb': '🌇',
            'Isha': '🌃'
        }
        return icons.get(self.prayer_name, '🕌')
    
    def load_notification_settings(self):
        """Load notification settings"""
        try:
            notifications_file = os.path.join(self.config_dir, 'notifications.json')
            if os.path.exists(notifications_file):
                with open(notifications_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Could not load notification settings: {e}")
        return {}
    
    def play_alarm_sound(self):
        """Play alarm sound if enabled"""
        if not self.sound_enabled:
            return
            
        try:
            # Try different system sounds
            sound_files = [
                '/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga',
                '/usr/share/sounds/freedesktop/stereo/message-new-instant.oga',
                '/usr/share/sounds/alsa/Front_Left.wav'
            ]
            
            for sound_file in sound_files:
                if os.path.exists(sound_file):
                    subprocess.Popen(['paplay', sound_file], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    break
            else:
                # Fallback: system beep
                print('\a' * 3)
        except Exception as e:
            print(f"Could not play alarm sound: {e}")
            print('\a' * 3)  # Fallback beep
    
    def flash_window(self):
        """Flash window border for attention"""
        if self.flash_state:
            self.setStyleSheet(self.get_alarm_stylesheet())
        else:
            flash_style = self.get_alarm_stylesheet().replace(
                "border: 3px solid #FFD700;",
                "border: 3px solid #FF4444;"
            )
            self.setStyleSheet(flash_style)
        self.flash_state = not self.flash_state
    
    def snooze_alarm(self):
        """Snooze the alarm"""
        self.stop_timers()
        
        # Schedule next alarm
        snooze_time = datetime.now() + timedelta(minutes=self.snooze_duration)
        
        # Show snooze notification
        try:
            subprocess.run([
                'notify-send', 
                f'🕌 {self.prayer_name} Prayer Snoozed',
                f'Will remind again at {snooze_time.strftime("%H:%M")}',
                '--urgency=low',
                '--expire-time=3000'
            ], check=False, timeout=2)
        except:
            pass
        
        self.accept()
        
        # Schedule snoozed alarm (this would need integration with main app)
        QTimer.singleShot(self.snooze_duration * 60 * 1000, 
                         lambda: self.show_snoozed_alarm())
    
    def show_snoozed_alarm(self):
        """Show snoozed alarm"""
        snoozed_dialog = PrayerAlarmDialog(
            self.prayer_name + " (Snoozed)", 
            self.prayer_time, 
            self.language
        )
        snoozed_dialog.exec_()
    
    def stop_alarm(self):
        """Stop the alarm"""
        self.stop_timers()
        self.accept()
    
    def auto_dismiss(self):
        """Auto dismiss after timeout"""
        self.stop_timers()
        self.accept()
    
    def stop_timers(self):
        """Stop all timers"""
        if hasattr(self, 'auto_close_timer'):
            self.auto_close_timer.stop()
        if hasattr(self, 'flash_timer'):
            self.flash_timer.stop()
    
    def closeEvent(self, event):
        """Handle close event"""
        self.stop_timers()
        super().closeEvent(event)

def show_prayer_alarm(prayer_name, prayer_time, language='en'):
    """Show prayer alarm dialog"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    alarm = PrayerAlarmDialog(prayer_name, prayer_time, language)
    return alarm.exec_()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Prayer Alarm Dialog')
    parser.add_argument('--prayer', default='Fajr', help='Prayer name')
    parser.add_argument('--time', default='05:30', help='Prayer time')
    parser.add_argument('--language', default='en', help='Language code')
    
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    
    alarm = PrayerAlarmDialog(args.prayer, args.time, args.language)
    sys.exit(alarm.exec_())