#!/usr/bin/env python3
import sys
import os
import json
import subprocess
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ultra_modern_salah import PrayerTimeWorker, CITIES, TRANSLATIONS
import os

class SalahTrayIndicator(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load config
        self.config_dir = os.path.join(os.path.expanduser('~'), '.salah_times', 'tray')
        self.config_file = os.path.join(os.path.expanduser('~'), '.salah_times', 'config', 'app_config.json')
        self.iqama_config_file = os.path.join(os.path.expanduser('~'), '.salah_times', 'config', 'iqama_times.json')
        self.notifications_config_file = os.path.join(os.path.expanduser('~'), '.salah_times', 'config', 'notifications.json')
        self.tray_config_file = os.path.join(self.config_dir, 'tray_config.json')
        os.makedirs(self.config_dir, exist_ok=True)
        self.ensure_iqama_config_exists()
        self.ensure_notifications_config_exists()
        self.current_language = self.load_main_config('language', 'en')
        self.current_city = self.load_main_config('city', 'Tangier')
        
        # Prayer data
        self.prayer_times = {}
        self.last_notification = None
        self.iqama_notification_sent = False
        self.notification_counts = {}  # Track notification repeats
        self.snoozed_prayers = {}  # Track snoozed prayers
        
        # Setup tray
        self.setup_tray()
        self.setup_timer()
        self.setup_config_watcher()
        self.load_prayer_times()
        
    def load_main_config(self, key, default):
        """Load from main app config"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get(key, default)
            except:
                pass
        return default
    
    def save_tray_config(self, key, value):
        """Save tray-specific configuration"""
        try:
            config = {}
            if os.path.exists(self.tray_config_file):
                with open(self.tray_config_file, 'r') as f:
                    config = json.load(f)
            
            config[key] = value
            
            with open(self.tray_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Could not save tray config: {e}")
    
    def load_tray_config(self, key, default):
        """Load tray-specific configuration"""
        try:
            if os.path.exists(self.tray_config_file):
                with open(self.tray_config_file, 'r') as f:
                    config = json.load(f)
                    return config.get(key, default)
        except Exception as e:
            print(f"Could not load tray config: {e}")
        return default
    
    def setup_tray(self):
        # Create tray icon
        icon = self.create_icon()
        self.setIcon(icon)
        
        # Create context menu
        self.menu = QMenu()
        
        # Title with city name
        self.title_action = QAction("🕌 Salah Times - Loading...", self)
        self.title_action.triggered.connect(lambda: None)
        font = self.title_action.font()
        font.setBold(True)
        self.title_action.setFont(font)
        self.menu.addAction(self.title_action)
        
        self.menu.addSeparator()
        
        # Date info
        self.date_action = QAction("📅 Loading date...", self)
        self.date_action.triggered.connect(lambda: None)
        self.menu.addAction(self.date_action)
        
        self.menu.addSeparator()
        
        # Prayer times (will be populated dynamically)
        self.prayer_actions = {}
        
        # Next prayer countdown
        self.menu.addSeparator()
        self.next_prayer_label = QAction("--- NEXT PRAYER ---", self)
        self.next_prayer_label.triggered.connect(lambda: None)
        font = self.next_prayer_label.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() - 1)
        self.next_prayer_label.setFont(font)
        self.menu.addAction(self.next_prayer_label)
        
        self.next_prayer_action = QAction("Loading...", self)
        self.next_prayer_action.triggered.connect(lambda: None)
        font = self.next_prayer_action.font()
        font.setBold(True)
        self.next_prayer_action.setFont(font)
        self.menu.addAction(self.next_prayer_action)
        
        self.countdown_action = QAction("⏰ 00:00:00 ⏰", self)
        self.countdown_action.triggered.connect(lambda: None)
        self.menu.addAction(self.countdown_action)
        
        # Iqama countdown
        self.iqama_action = QAction("", self)
        self.iqama_action.triggered.connect(lambda: None)
        self.menu.addAction(self.iqama_action)
        
        self.menu.addSeparator()
        
        # Controls
        refresh_action = QAction("↻ Refresh", self)
        refresh_action.triggered.connect(self.refresh_prayer_times)
        self.menu.addAction(refresh_action)
        
        # Settings (opens main app)
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.show_main_app)
        self.menu.addAction(settings_action)
        
        self.menu.addSeparator()
        
        # Quit
        quit_action = QAction("❌ Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        self.menu.addAction(quit_action)
        
        # Apply dark theme to menu
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 20px;
                border-radius: 4px;
                color: white;
            }
            QMenu::item:selected {
                background-color: #404040;
                color: white;
            }
            QMenu::item:disabled {
                color: white;
                background-color: transparent;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555;
                margin: 5px 10px;
            }
        """)
        
        self.setContextMenu(self.menu)
        
        # Show tray icon
        self.show()
        
        # Set tooltip
        self.update_tooltip()
    
    def create_icon(self):
        # Create a simple mosque icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw mosque silhouette
        painter.setPen(QPen(QColor(45, 90, 39), 2))
        painter.setBrush(QBrush(QColor(45, 90, 39)))
        
        # Main dome
        painter.drawEllipse(8, 8, 16, 12)
        
        # Minaret
        painter.drawRect(4, 12, 4, 16)
        painter.drawRect(24, 12, 4, 16)
        
        # Base
        painter.drawRect(6, 20, 20, 8)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def setup_timer(self):
        # Timer for checking prayer times and notifications
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_notifications)
        self.timer.start(60000)  # Check every minute (less frequent)
        
        # Timer for updating tooltip and menu
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second for live countdown
        
        # Timer to reload cache periodically
        self.cache_timer = QTimer()
        self.cache_timer.timeout.connect(self.load_prayer_times)
        self.cache_timer.start(300000)  # Check cache every 5 minutes
    
    def setup_config_watcher(self):
        # Timer to check for config file changes
        self.config_watcher = QTimer()
        self.config_watcher.timeout.connect(self.check_config_changes)
        self.config_watcher.start(2000)  # Check every 2 seconds
        self.last_config_mtime = self.get_config_mtime()
    
    def get_config_mtime(self):
        try:
            return os.path.getmtime(self.config_file) if os.path.exists(self.config_file) else 0
        except:
            return 0
    
    def check_config_changes(self):
        current_mtime = self.get_config_mtime()
        if current_mtime != self.last_config_mtime:
            self.last_config_mtime = current_mtime
            new_language = self.load_main_config('language', 'en')
            new_city = self.load_main_config('city', 'Tangier')
            
            if new_language != self.current_language or new_city != self.current_city:
                self.current_language = new_language
                self.current_city = new_city
                self.load_prayer_times()  # Refresh prayer times
    
    def load_prayer_times(self):
        """Load prayer times from main app's cache only"""
        try:
            # Load from main app's cities cache ONLY
            cities_folder = os.path.join(os.path.expanduser('~'), '.salah_times', 'cities')
            city_file = os.path.join(cities_folder, f'{self.current_city.lower()}.json')
            
            if os.path.exists(city_file):
                with open(city_file, 'r', encoding='utf-8') as f:
                    city_data = json.load(f)
                    today = datetime.now().strftime('%d/%m')
                    if today in city_data['prayer_times']:
                        self.prayer_times = city_data['prayer_times'][today]
                        print(f"Tray: Loaded cached prayer times for {self.current_city}")
                        self.on_prayer_times_loaded(self.prayer_times)
                        return
            
            # No cache available - use empty times (don't fetch)
            print(f"Tray: No cached data for {self.current_city}, waiting for main app")
            self.prayer_times = {}
            
        except Exception as e:
            print(f"Tray: Error loading prayer times: {e}")
            self.prayer_times = {}
    
    def refresh_prayer_times(self):
        """Refresh prayer times without closing the menu"""
        # Update the refresh button text to show it's working
        for action in self.menu.actions():
            if "Refresh" in action.text():
                action.setText("🔄 Refreshing...")
                break
        
        # Load new prayer times
        self.load_prayer_times()
        
        # Reset refresh button text after a short delay
        QTimer.singleShot(2000, self.reset_refresh_button)
    
    def reset_refresh_button(self):
        """Reset the refresh button text"""
        for action in self.menu.actions():
            if "Refreshing" in action.text():
                action.setText("↻ Refresh")
                break
    
    def on_prayer_times_loaded(self, prayer_times, days_remaining=None):
        self.prayer_times = prayer_times
        self.update_prayer_menu()
        self.update_display()
        # Reset notification flags when new data is loaded
        self.notification_counts = {}
        # Cancel all pending timers
        if hasattr(self, 'prayer_timers'):
            for prayer, timers in self.prayer_timers.items():
                for timer in timers:
                    if timer.isActive():
                        timer.stop()
            self.prayer_timers = {}
    
    def on_error(self, error):
        self.setToolTip(f"Salah Times - Error: {error}")
    
    def update_tooltip(self):
        if not self.prayer_times:
            self.setToolTip("🕌 Salah Times - Loading...")
            return
        
        city_name = self.tr_city(self.current_city)
        tooltip = f"🕌 {self.tr('app_title')} - {city_name}\n"
        tooltip += "─" * 30 + "\n"
        
        # Add today's prayer times
        icons = {'Fajr': '☽', 'Sunrise': '☀', 'Dohr': '☉', 
                'Asr': '☀', 'Maghreb': '☾', 'Isha': '★'}
        
        current_prayer = self.get_current_prayer()
        
        for prayer in ['Fajr', 'Sunrise', 'Dohr', 'Asr', 'Maghreb', 'Isha']:
            if prayer in self.prayer_times:
                icon = icons.get(prayer, '🕐')
                prayer_name = self.tr_prayer(prayer)
                prayer_time = self.prayer_times[prayer]
                
                if prayer == current_prayer:
                    tooltip += f"► {icon} {prayer_name}: {prayer_time} ◄\n"
                else:
                    tooltip += f"  {icon} {prayer_name}: {prayer_time}\n"
        
        tooltip += "─" * 30 + "\n"
        
        # Next prayer info
        next_prayer = self.get_next_prayer()
        if next_prayer:
            prayer_name = self.tr_prayer(next_prayer)
            prayer_time = self.prayer_times[next_prayer]
            countdown = self.get_live_countdown_to_prayer(next_prayer)
            
            # Check if it's tomorrow's prayer
            now = datetime.now()
            current_time = now.hour * 60 + now.minute
            prayer_time_minutes = self.parse_time(prayer_time)
            
            if prayer_time_minutes <= current_time:
                tooltip += f"Next: {prayer_name} ({self.tr('tomorrow')}) at {prayer_time}\n"
            else:
                tooltip += f"Next: {prayer_name} at {prayer_time}\n"
            
            tooltip += f"Time left: {countdown}\n"
        
        # Add current prayer Iqama info if applicable
        if current_prayer and self.is_iqama_time(current_prayer):
            iqama_countdown = self.get_live_iqama_countdown(current_prayer)
            tooltip += f"\n⏰ Iqama {self.tr_prayer(current_prayer)}: {iqama_countdown}"
        
        self.setToolTip(tooltip)
    
    def update_prayer_menu(self):
        if not self.prayer_times:
            return
        
        # Update title with city
        city_name = self.tr_city(self.current_city)
        self.title_action.setText(f"🕌 {self.tr('app_title')} - {city_name}")
        
        # Update date
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        self.date_action.setText(f"📅 {date_str}")
        
        # Remove existing prayer actions
        for action in self.prayer_actions.values():
            self.menu.removeAction(action)
        self.prayer_actions.clear()
        
        # Add prayer times
        icons = {'Fajr': '☽', 'Sunrise': '☀', 'Dohr': '☉', 
                'Asr': '☀', 'Maghreb': '☾', 'Isha': '★'}
        
        current_prayer = self.get_current_prayer()
        
        # Find position to insert prayer actions (after date separator)
        date_index = 0
        for i, action in enumerate(self.menu.actions()):
            if action == self.date_action:
                date_index = i + 2  # After date and separator
                break
        
        insert_index = date_index
        for prayer in ['Fajr', 'Sunrise', 'Dohr', 'Asr', 'Maghreb', 'Isha']:
            if prayer in self.prayer_times:
                icon = icons.get(prayer, '🕐')
                prayer_name = self.tr_prayer(prayer)
                prayer_time = self.prayer_times[prayer]
                
                action_text = f"{icon} {prayer_name:<8} {prayer_time}"
                
                action = QAction(action_text, self)
                action.triggered.connect(lambda checked, p=prayer: self.on_prayer_clicked(p))
                
                # Highlight current prayer
                if prayer == current_prayer:
                    font = action.font()
                    font.setBold(True)
                    action.setFont(font)
                
                self.menu.insertAction(self.menu.actions()[insert_index], action)
                self.prayer_actions[prayer] = action
                insert_index += 1
    
    def update_display(self):
        self.update_tooltip()
        self.update_countdown_display()
    
    def update_countdown_display(self):
        if not self.prayer_times:
            return
        
        # Update next prayer info
        next_prayer = self.get_next_prayer()
        if next_prayer:
            prayer_name = self.tr_prayer(next_prayer)
            prayer_time = self.prayer_times[next_prayer]
            
            # Check if it's tomorrow's prayer
            now = datetime.now()
            current_time = now.hour * 60 + now.minute
            prayer_time_minutes = self.parse_time(prayer_time)
            
            if prayer_time_minutes <= current_time:
                prayer_display = f"{prayer_name} ({self.tr('tomorrow')})"
            else:
                prayer_display = prayer_name
            
            self.next_prayer_action.setText(f"{prayer_display} - {prayer_time}")
            
            # Update countdown
            countdown = self.get_live_countdown_to_prayer(next_prayer)
            self.countdown_action.setText(f"⏰ {countdown} ⏰")
        else:
            self.next_prayer_action.setText("No prayer data")
            self.countdown_action.setText("⏰ 00:00:00 ⏰")
        
        # Update Iqama countdown
        current_prayer = self.get_current_prayer()
        if current_prayer and self.is_iqama_time(current_prayer):
            iqama_countdown = self.get_live_iqama_countdown(current_prayer)
            iqama_time = self.get_iqama_time(current_prayer)
            prayer_name = self.tr_prayer(current_prayer)
            self.iqama_action.setText(f"⏰ Iqama {prayer_name} at {iqama_time}: {iqama_countdown}")
            self.iqama_action.setVisible(True)
        else:
            self.iqama_action.setText("")
            self.iqama_action.setVisible(False)
    
    def check_notifications(self):
        if not self.prayer_times:
            return
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        current_minute_key = f"{now.hour:02d}:{now.minute:02d}"
        
        prayers = [name for name in self.prayer_times.keys() if name != 'Date']
        notification_settings = self.load_notification_settings()
        
        for prayer in prayers:
            if prayer in self.prayer_times:
                prayer_time_str = self.prayer_times[prayer]
                prayer_time = self.parse_time(prayer_time_str)
                
                # Check if notifications are enabled for this prayer
                prayer_config = notification_settings.get(prayer, {'enabled': True, 'repeat_count': 3})
                if not prayer_config.get('enabled', True):
                    continue
                
                # Prayer time notification - trigger only once per minute
                if current_time == prayer_time:
                    if prayer not in self.notification_counts:
                        max_repeats = prayer_config.get('repeat_count', 3)
                        self.notification_counts[prayer] = 1
                        self.send_prayer_notification_immediate(prayer)
                        
                        # Schedule repeats if configured
                        if max_repeats > 1:
                            self.schedule_repeat_notifications(prayer, max_repeats)
                
                # Reset notification count after prayer time window
                elif current_time > prayer_time + 5:  # 5 minutes after prayer
                    if prayer in self.notification_counts:
                        del self.notification_counts[prayer]
                        # Cancel any pending timers for this prayer
                        self.cancel_prayer_timers(prayer)
    
    def schedule_repeat_notifications(self, prayer, max_repeats):
        """Schedule repeat notifications for a prayer"""
        notification_settings = self.load_notification_settings()
        interval_minutes = notification_settings.get('notification_interval', 2)
        interval_ms = interval_minutes * 60 * 1000
        
        # Store timers to allow cancellation
        if not hasattr(self, 'prayer_timers'):
            self.prayer_timers = {}
        
        self.prayer_timers[prayer] = []
        
        for repeat_num in range(2, max_repeats + 1):  # Start from 2nd notification
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda p=prayer, n=repeat_num: self.send_repeat_notification(p, n))
            timer.start((repeat_num - 1) * interval_ms)
            self.prayer_timers[prayer].append(timer)
    
    def send_repeat_notification(self, prayer, repeat_num):
        """Send a repeat notification"""
        if prayer in self.notification_counts:  # Only if not cancelled
            notification_settings = self.load_notification_settings()
            prayer_config = notification_settings.get(prayer, {'repeat_count': 3})
            max_repeats = prayer_config.get('repeat_count', 3)
            
            # Only send if we haven't exceeded the configured repeat count
            if repeat_num <= max_repeats:
                self.notification_counts[prayer] = repeat_num
                self.send_prayer_notification_immediate(prayer)
            else:
                # Clean up if we've reached the limit
                del self.notification_counts[prayer]
                self.cancel_prayer_timers(prayer)
    
    def cancel_prayer_timers(self, prayer):
        """Cancel all pending timers for a prayer"""
        if hasattr(self, 'prayer_timers') and prayer in self.prayer_timers:
            for timer in self.prayer_timers[prayer]:
                if timer.isActive():
                    timer.stop()
            del self.prayer_timers[prayer]
    
    def send_prayer_notification_immediate(self, prayer):
        """Send immediate system notification with sound"""
        try:
            prayer_name = self.tr_prayer(prayer)
            prayer_time = self.prayer_times[prayer]
            iqama_time = self.get_iqama_time(prayer)
            iqama_delay = self.get_iqama_delay(prayer)
            
            # Get repeat info
            repeat_info = ""
            if prayer in self.notification_counts:
                notification_settings = self.load_notification_settings()
                max_repeats = notification_settings.get(prayer, {}).get('repeat_count', 3)
                current_count = self.notification_counts[prayer]
                repeat_info = f" ({current_count}/{max_repeats})"
            
            # Play sound immediately BEFORE notification
            self.play_system_sound()
            
            # Send system notification with actions
            subprocess.run([
                'notify-send',
                f'🕌 {prayer_name} Prayer Time{repeat_info}',
                f'It\'s time for {prayer_name} prayer\nIqama at {iqama_time} (in {iqama_delay} minutes)',
                '--urgency=critical',
                '--expire-time=0',  # Don't auto-expire
                '--icon=appointment-soon',
                '--action=stop=⏹️ Stop All'
            ], check=False, timeout=2)
            
        except Exception as e:
            print(f"Could not send system notification: {e}")
            # Fallback to tray notification
            self.send_prayer_notification(prayer)
    
    def send_prayer_notification(self, prayer):
        """Send regular tray notification (fallback)"""
        prayer_name = self.tr_prayer(prayer)
        iqama_time = self.get_iqama_time(prayer)
        iqama_delay = self.get_iqama_delay(prayer)
        
        repeat_info = ""
        if prayer in self.notification_counts:
            notification_settings = self.load_notification_settings()
            max_repeats = notification_settings.get(prayer, {}).get('repeat_count', 3)
            current_count = self.notification_counts[prayer]
            repeat_info = f" ({current_count}/{max_repeats})"
        
        self.showMessage(
            f"🕌 {prayer_name} Prayer Time{repeat_info}",
            f"It's time for {prayer_name} prayer\nIqama at {iqama_time} (in {iqama_delay} minutes)",
            QSystemTrayIcon.Information,
            8000
        )
        
        self.play_system_sound()
    
    def stop_all_notifications(self, prayer):
        """Stop all notifications for a prayer"""
        if prayer in self.notification_counts:
            del self.notification_counts[prayer]
        self.cancel_prayer_timers(prayer)
        print(f"Stopped all notifications for {prayer}")
    
    def play_system_sound(self):
        """Play system sound if enabled"""
        notification_settings = self.load_notification_settings()
        if not notification_settings.get('sound_enabled', True):
            return
            
        try:
            # Try alarm sound first
            subprocess.run(['paplay', '/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga'], 
                         check=False, timeout=3)
        except:
            try:
                # Fallback to message sound
                subprocess.run(['paplay', '/usr/share/sounds/freedesktop/stereo/message-new-instant.oga'], 
                             check=False, timeout=3)
            except:
                # Final fallback: system beep
                print('\a')
    
    def on_prayer_clicked(self, prayer):
        """Handle prayer time click - currently does nothing but is clickable"""
        pass
    
    def show_main_app(self):
        try:
            # Launch the main application
            script_dir = os.path.dirname(os.path.abspath(__file__))
            main_app_path = os.path.join(script_dir, 'ultra_modern_salah.py')
            subprocess.Popen([sys.executable, main_app_path])
        except Exception as e:
            self.showMessage("Error", f"Could not open main app: {e}", QSystemTrayIcon.Critical)
    
    def get_next_prayer(self):
        if not self.prayer_times:
            return None
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        
        prayers = [name for name in self.prayer_times.keys() if name != 'Date']
        
        for prayer in prayers:
            if prayer in self.prayer_times:
                prayer_time = self.parse_time(self.prayer_times[prayer])
                if prayer_time > current_time:
                    return prayer
        
        # If no prayer today, return first prayer (Fajr) for tomorrow
        return prayers[0] if prayers else None
    
    def get_current_prayer(self):
        if not self.prayer_times:
            return None
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        
        prayers = [name for name in self.prayer_times.keys() if name != 'Date']
        
        for i, prayer in enumerate(prayers):
            if prayer in self.prayer_times:
                prayer_time = self.parse_time(self.prayer_times[prayer])
                next_prayer_time = None
                
                if i < len(prayers) - 1:
                    next_prayer = prayers[i + 1]
                    if next_prayer in self.prayer_times:
                        next_prayer_time = self.parse_time(self.prayer_times[next_prayer])
                else:
                    next_prayer_time = 24 * 60
                
                if next_prayer_time and prayer_time <= current_time < next_prayer_time:
                    return prayer
        
        return None
    
    def get_countdown_to_prayer(self, prayer):
        if not prayer or prayer not in self.prayer_times:
            return "00:00:00"
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        prayer_time = self.parse_time(self.prayer_times[prayer])
        
        if prayer_time > current_time:
            remaining = prayer_time - current_time
        else:
            # Tomorrow's prayer
            remaining = (24 * 60) - current_time + prayer_time
        
        hours = remaining // 60
        minutes = remaining % 60
        
        return f"{hours:02d}:{minutes:02d}"
    
    def get_live_countdown_to_prayer(self, prayer):
        if not prayer or prayer not in self.prayer_times:
            return "00:00:00"
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        current_seconds = now.second
        prayer_time = self.parse_time(self.prayer_times[prayer])
        
        if prayer_time > current_time:
            remaining = prayer_time - current_time
        else:
            # Tomorrow's prayer - calculate time until tomorrow's prayer
            minutes_until_midnight = (24 * 60) - current_time
            remaining = minutes_until_midnight + prayer_time
        
        hours = remaining // 60
        minutes = remaining % 60
        seconds = 60 - current_seconds if current_seconds > 0 else 0
        
        if seconds == 60:
            seconds = 0
        elif seconds > 0 and minutes > 0:
            minutes -= 1
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_iqama_countdown(self, prayer):
        if not prayer or prayer not in self.prayer_times:
            return "00:00:00"
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        prayer_time = self.parse_time(self.prayer_times[prayer])
        iqama_delay = self.get_iqama_delay(prayer)
        iqama_end_time = prayer_time + iqama_delay
        
        remaining = iqama_end_time - current_time
        
        if remaining <= 0:
            return "00:00:00"
        
        hours = remaining // 60
        minutes = remaining % 60
        
        return f"{hours:02d}:{minutes:02d}"
    
    def get_live_iqama_countdown(self, prayer):
        if not prayer or prayer not in self.prayer_times:
            return "00:00:00"
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        current_seconds = now.second
        prayer_time = self.parse_time(self.prayer_times[prayer])
        iqama_delay = self.get_iqama_delay(prayer)
        iqama_end_time = prayer_time + iqama_delay
        
        remaining = iqama_end_time - current_time
        
        if remaining <= 0:
            return "00:00:00"
        
        hours = remaining // 60
        minutes = remaining % 60
        seconds = 60 - current_seconds if current_seconds > 0 else 0
        
        if seconds == 60:
            seconds = 0
        elif seconds > 0 and minutes > 0:
            minutes -= 1
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def is_iqama_time(self, prayer):
        if not prayer or prayer not in self.prayer_times:
            return False
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        prayer_time = self.parse_time(self.prayer_times[prayer])
        iqama_delay = self.get_iqama_delay(prayer)
        
        return prayer_time <= current_time < prayer_time + iqama_delay
    
    def ensure_iqama_config_exists(self):
        """Create Iqama config with defaults if it doesn't exist"""
        if not os.path.exists(self.iqama_config_file):
            try:
                config_dir = os.path.dirname(self.iqama_config_file)
                os.makedirs(config_dir, exist_ok=True)
                default_iqama = {'Fajr': 20, 'Dohr': 15, 'Asr': 15, 'Maghreb': 10, 'Isha': 15}
                with open(self.iqama_config_file, 'w') as f:
                    json.dump(default_iqama, f, indent=2)
            except Exception as e:
                print(f"Could not create default Iqama config: {e}")
    
    def load_iqama_times(self):
        """Load Iqama times from config"""
        try:
            with open(self.iqama_config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Could not load Iqama times: {e}")
            return {'Fajr': 20, 'Dohr': 15, 'Asr': 15, 'Maghreb': 10, 'Isha': 15}
    
    def ensure_notifications_config_exists(self):
        """Create notifications config with defaults if it doesn't exist"""
        if not os.path.exists(self.notifications_config_file):
            try:
                config_dir = os.path.dirname(self.notifications_config_file)
                os.makedirs(config_dir, exist_ok=True)
                default_notifications = {
                    'sound_enabled': True,
                    'snooze_duration': 5,
                    'notification_interval': 2,
                    'Fajr': {'enabled': True, 'repeat_count': 3},
                    'Dohr': {'enabled': True, 'repeat_count': 3},
                    'Asr': {'enabled': True, 'repeat_count': 3},
                    'Maghreb': {'enabled': True, 'repeat_count': 3},
                    'Isha': {'enabled': True, 'repeat_count': 3}
                }
                with open(self.notifications_config_file, 'w') as f:
                    json.dump(default_notifications, f, indent=2)
            except Exception as e:
                print(f"Could not create default notifications config: {e}")
    
    def load_notification_settings(self):
        """Load notification settings from config"""
        try:
            with open(self.notifications_config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Could not load notification settings: {e}")
            return {'sound_enabled': True, 'snooze_duration': 5, 'notification_interval': 2}
    
    def get_iqama_delay(self, prayer):
        """Get Iqama delay from config"""
        iqama_times = self.load_iqama_times()
        return iqama_times.get(prayer, 15)
    
    def get_iqama_time(self, prayer):
        if not prayer or prayer not in self.prayer_times:
            return "00:00"
        
        prayer_time = self.parse_time(self.prayer_times[prayer])
        iqama_delay = self.get_iqama_delay(prayer)
        iqama_time_minutes = prayer_time + iqama_delay
        
        hours = iqama_time_minutes // 60
        minutes = iqama_time_minutes % 60
        
        return f"{hours:02d}:{minutes:02d}"
    
    def parse_time(self, time_str):
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except:
            return 0
    
    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)
    
    def tr_prayer(self, prayer_key):
        return TRANSLATIONS[self.current_language]['prayers'].get(prayer_key, prayer_key)
    
    def tr_city(self, city_key):
        return CITIES[city_key][self.current_language]

class SalahTrayApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", 
                               "System tray is not available on this system.")
            sys.exit(1)
        
        # Prevent app from quitting when last window is closed
        self.setQuitOnLastWindowClosed(False)
        
        # Create tray indicator
        self.tray = SalahTrayIndicator()
        
        # Show startup message
        self.tray.showMessage(
            "🕌 Salah Times Tray",
            "Prayer times indicator is now running in system tray\nRight-click for full prayer schedule",
            QSystemTrayIcon.Information,
            4000
        )

def main():
    app = SalahTrayApp(sys.argv)
    
    # Set application properties
    app.setApplicationName("Salah Times Tray")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Islamic Apps")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()