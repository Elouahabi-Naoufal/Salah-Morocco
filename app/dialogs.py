import os
import json
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .constants import TRANSLATIONS, CITIES

class SettingsDialog(QDialog):
    def __init__(self, current_city, current_language, parent=None):
        super().__init__(parent)
        self.current_city = current_city
        self.current_language = current_language
        self.cities = sorted(CITIES.keys())
        self.config_dir = os.path.join(os.path.expanduser('~'), '.salah_times', 'config')
        self.geometry_file = os.path.join(self.config_dir, 'settings_geometry.json')
        self.iqama_config_file = os.path.join(self.config_dir, 'iqama_times.json')
        self.notifications_config_file = os.path.join(self.config_dir, 'notifications.json')
        self.iqama_times = self.load_iqama_times()
        self.notification_settings = self.load_notification_settings()
        self.init_ui()
        self.restore_geometry()
        
    def init_ui(self):
        self.setWindowTitle(self.tr('settings'))
        self.setMinimumSize(750, 800)
        self.resize(800, 850)
        self.setModal(True)
        self.setStyleSheet(self.get_modern_settings_stylesheet())
        
        # Main container with gradient background
        main_container = QWidget()
        main_container.setObjectName("settings_main")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_container)
        
        layout = QVBoxLayout(main_container)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Header section
        header = self.create_settings_header()
        layout.addWidget(header, 0)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setProperty("class", "settings_tabs")
        
        # General tab
        general_tab = self.create_general_tab()
        self.tab_widget.addTab(general_tab, "⚙️ General")
        
        # Iqama tab
        iqama_tab = self.create_iqama_tab()
        self.tab_widget.addTab(iqama_tab, "⏰ Iqama Times")
        
        # Notifications tab
        notifications_tab = self.create_notifications_tab()
        self.tab_widget.addTab(notifications_tab, "🔔 Notifications")
        
        layout.addWidget(self.tab_widget, 1)
        
        # Button section
        button_section = self.create_button_section()
        layout.addWidget(button_section, 0)
    
    def get_modern_settings_stylesheet(self):
        return """
            #settings_main {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fffe, stop:1 #e8f5e8);
            }
            
            .settings_card {
                background: white;
                border-radius: 15px;
                border: 1px solid rgba(45, 90, 39, 0.1);
                padding: 20px;
            }
            
            .settings_title {
                color: #2d5a27;
                font-size: 28px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            .settings_subtitle {
                color: #666666;
                font-size: 14px;
                font-weight: 400;
            }
            
            .section_label {
                color: #2d5a27;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 10px;
            }
            
            .modern_combo {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 12px 15px;
                font-size: 14px;
                color: #333;
                min-height: 20px;
            }
            
            .modern_combo:focus {
                border-color: #2d5a27;
                outline: none;
            }
            
            .modern_combo::drop-down {
                border: none;
                width: 30px;
            }
            
            .modern_combo::down-arrow {
                image: none;
                border: 2px solid #666;
                border-top: none;
                border-right: none;
                width: 8px;
                height: 8px;
                transform: rotate(-45deg);
                margin-right: 10px;
            }
            
            .modern_search {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 12px 15px;
                font-size: 14px;
                color: #333;
            }
            
            .modern_search:focus {
                border-color: #2d5a27;
                outline: none;
            }
            
            .modern_list {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                font-size: 14px;
                color: #333;
                outline: none;
            }
            
            .modern_list::item {
                padding: 12px 15px;
                border-bottom: 1px solid #f0f0f0;
            }
            
            .modern_list::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a7c59, stop:1 #2d5a27);
                color: white;
            }
            
            .modern_list::item:hover {
                background: rgba(45, 90, 39, 0.1);
            }
            
            .modern_button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4a7c59, stop:1 #2d5a27);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 28px;
                font-size: 14px;
                font-weight: 600;
            }
            
            .modern_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a8c69, stop:1 #3d6a37);
            }
            
            .cancel_button {
                background: #f5f5f5;
                color: #666;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 14px 28px;
                font-size: 14px;
                font-weight: 600;
            }
            
            .cancel_button:hover {
                background: #e8e8e8;
                border-color: #ccc;
            }
            
            .settings_tabs {
                background: transparent;
                border: none;
            }
            
            .settings_tabs::pane {
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                background: white;
                padding: 15px;
            }
            
            .settings_tabs::tab-bar {
                alignment: center;
            }
            
            .settings_tabs QTabBar::tab {
                background: #f5f5f5;
                border: 2px solid #e0e0e0;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                padding: 15px 25px;
                margin-right: 3px;
                font-size: 15px;
                font-weight: 500;
                color: #666;
                min-width: 120px;
            }
            
            .settings_tabs QTabBar::tab:selected {
                background: white;
                border-color: #2d5a27;
                color: #2d5a27;
                font-weight: 600;
            }
            
            .settings_tabs QTabBar::tab:hover {
                background: #f0f8f0;
                color: #2d5a27;
            }
            
            .iqama_input {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: #333;
                min-width: 120px;
                max-width: 150px;
            }
            
            .iqama_input:focus {
                border-color: #2d5a27;
                outline: none;
            }
            
            .iqama_label {
                color: #2d5a27;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }
            
            .modern_button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4a7c59, stop:1 #2d5a27);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 28px;
                font-size: 14px;
                font-weight: 600;
            }
            
            .modern_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a8c69, stop:1 #3d6a37);
            }
        """
    
    def create_settings_header(self):
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        title = QLabel(self.tr('settings'))
        title.setProperty("class", "settings_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Customize your prayer times experience")
        subtitle.setProperty("class", "settings_subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        return header
    
    def create_language_section(self):
        section = QWidget()
        section.setProperty("class", "settings_card")
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        label = QLabel(self.tr('language'))
        label.setProperty("class", "section_label")
        layout.addWidget(label)
        
        self.language_combo = QComboBox()
        self.language_combo.setProperty("class", "modern_combo")
        self.language_combo.addItems(['English', 'العربية', 'Français'])
        lang_map = {'en': 0, 'ar': 1, 'fr': 2}
        self.language_combo.setCurrentIndex(lang_map.get(self.current_language, 0))
        layout.addWidget(self.language_combo)
        
        return section
    
    def create_city_section(self):
        section = QWidget()
        section.setProperty("class", "settings_card")
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        label = QLabel(self.tr('select_city'))
        label.setProperty("class", "section_label")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        self.search_box = QLineEdit()
        self.search_box.setProperty("class", "modern_search")
        self.search_box.setPlaceholderText(self.tr('search_city'))
        self.search_box.textChanged.connect(self.filter_cities)
        layout.addWidget(self.search_box)
        
        self.city_list = QListWidget()
        self.city_list.setProperty("class", "modern_list")
        translated_cities = self.get_translated_cities()
        self.city_list.addItems(translated_cities)
        current_translated = CITIES[self.current_city][self.current_language]
        try:
            self.city_list.setCurrentRow(translated_cities.index(current_translated))
        except ValueError:
            self.city_list.setCurrentRow(0)
        layout.addWidget(self.city_list, 1)
        
        return section
    
    def create_button_section(self):
        section = QWidget()
        layout = QHBoxLayout(section)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        cancel_btn = QPushButton(self.tr('cancel'))
        cancel_btn.setProperty("class", "cancel_button")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton(self.tr('set_default'))
        ok_btn.setProperty("class", "modern_button")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(ok_btn)
        
        return section
    
    def create_general_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Language section
        lang_section = self.create_language_section()
        layout.addWidget(lang_section)
        
        # City section
        city_section = self.create_city_section()
        layout.addWidget(city_section, 1)
        
        return tab
    
    def create_iqama_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Configure Iqama Delay Times")
        title.setProperty("class", "section_label")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Set the delay time (in minutes) between Adhan and Iqama for each prayer:")
        desc.setStyleSheet("color: #666; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Iqama times card
        iqama_card = QWidget()
        iqama_card.setProperty("class", "settings_card")
        
        card_layout = QVBoxLayout(iqama_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(15)
        
        # Iqama inputs
        self.iqama_inputs = {}
        prayers = ['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha']
        icons = {'Fajr': '☽', 'Dohr': '☉', 'Asr': '☀', 'Maghreb': '☾', 'Isha': '★'}
        
        for prayer in prayers:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(15)
            
            # Prayer icon and name
            prayer_info = QWidget()
            info_layout = QHBoxLayout(prayer_info)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(8)
            
            icon_label = QLabel(icons[prayer])
            icon_label.setStyleSheet("font-size: 18px;")
            info_layout.addWidget(icon_label)
            
            name_label = QLabel(self.tr_prayer(prayer))
            name_label.setProperty("class", "iqama_label")
            info_layout.addWidget(name_label)
            info_layout.addStretch()
            
            row_layout.addWidget(prayer_info, 1)
            
            # Input and label
            input_widget = QSpinBox()
            input_widget.setProperty("class", "iqama_input")
            input_widget.setMinimum(0)
            input_widget.setMaximum(60)
            input_widget.setSuffix(" min")
            input_widget.setValue(self.iqama_times.get(prayer, self.get_default_iqama(prayer)))
            self.iqama_inputs[prayer] = input_widget
            
            row_layout.addWidget(input_widget)
            
            card_layout.addWidget(row)
        
        layout.addWidget(iqama_card, 1)
        
        # Reset button
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.setProperty("class", "cancel_button")
        reset_btn.clicked.connect(self.reset_iqama_times)
        reset_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        
        return tab
    
    def create_notifications_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Prayer notifications section
        prayer_section = QWidget()
        prayer_section.setProperty("class", "settings_card")
        
        prayer_layout = QVBoxLayout(prayer_section)
        prayer_layout.setContentsMargins(20, 20, 20, 20)
        prayer_layout.setSpacing(15)
        
        # Title
        title = QLabel("Prayer Notification Settings")
        title.setProperty("class", "section_label")
        prayer_layout.addWidget(title)
        
        # Description
        desc = QLabel("Configure notifications for each prayer:")
        desc.setStyleSheet("color: #666; font-size: 12px;")
        prayer_layout.addWidget(desc)
        
        # Prayer settings grid
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(10)
        grid.setContentsMargins(0, 10, 0, 0)
        
        # Headers
        grid.addWidget(QLabel("Prayer"), 0, 0)
        grid.addWidget(QLabel("Enable"), 0, 1)
        grid.addWidget(QLabel("Repeat"), 0, 2)
        
        # Prayer rows
        self.notification_inputs = {}
        prayers = ['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha']
        icons = {'Fajr': '☽', 'Dohr': '☉', 'Asr': '☀', 'Maghreb': '☾', 'Isha': '★'}
        
        for i, prayer in enumerate(prayers, 1):
            # Prayer name with icon
            prayer_widget = QWidget()
            prayer_widget_layout = QHBoxLayout(prayer_widget)
            prayer_widget_layout.setContentsMargins(0, 0, 0, 0)
            prayer_widget_layout.setSpacing(8)
            
            icon_label = QLabel(icons[prayer])
            icon_label.setStyleSheet("font-size: 16px;")
            prayer_widget_layout.addWidget(icon_label)
            
            name_label = QLabel(self.tr_prayer(prayer))
            name_label.setStyleSheet("font-weight: 500;")
            prayer_widget_layout.addWidget(name_label)
            prayer_widget_layout.addStretch()
            
            grid.addWidget(prayer_widget, i, 0)
            
            # Enable checkbox
            enable_checkbox = QCheckBox()
            enable_checkbox.setChecked(self.notification_settings.get(prayer, {}).get('enabled', True))
            grid.addWidget(enable_checkbox, i, 1)
            
            # Repeat count
            repeat_spinbox = QSpinBox()
            repeat_spinbox.setProperty("class", "iqama_input")
            repeat_spinbox.setMinimum(1)
            repeat_spinbox.setMaximum(10)
            repeat_spinbox.setValue(self.notification_settings.get(prayer, {}).get('repeat_count', 3))
            repeat_spinbox.setSuffix(" times")
            repeat_spinbox.setFixedWidth(120)
            grid.addWidget(repeat_spinbox, i, 2)
            
            self.notification_inputs[prayer] = {
                'enabled': enable_checkbox,
                'repeat_count': repeat_spinbox
            }
        
        prayer_layout.addWidget(grid_widget)
        layout.addWidget(prayer_section)
        
        # Sound settings section (compact)
        sound_section = QWidget()
        sound_section.setProperty("class", "settings_card")
        
        sound_layout = QVBoxLayout(sound_section)
        sound_layout.setContentsMargins(20, 15, 20, 15)
        sound_layout.setSpacing(10)
        
        sound_title = QLabel("Sound & Timing")
        sound_title.setProperty("class", "section_label")
        sound_layout.addWidget(sound_title)
        
        # Horizontal layout for all settings
        settings_row = QWidget()
        settings_layout = QHBoxLayout(settings_row)
        settings_layout.setSpacing(20)
        
        # Sound enabled
        self.sound_enabled = QCheckBox("Enable sounds")
        self.sound_enabled.setChecked(self.notification_settings.get('sound_enabled', True))
        settings_layout.addWidget(self.sound_enabled)
        
        # Snooze duration
        settings_layout.addWidget(QLabel("Snooze:"))
        self.snooze_duration = QSpinBox()
        self.snooze_duration.setProperty("class", "iqama_input")
        self.snooze_duration.setMinimum(1)
        self.snooze_duration.setMaximum(30)
        self.snooze_duration.setValue(self.notification_settings.get('snooze_duration', 5))
        self.snooze_duration.setSuffix(" min")
        self.snooze_duration.setFixedWidth(100)
        settings_layout.addWidget(self.snooze_duration)
        
        # Notification interval
        settings_layout.addWidget(QLabel("Interval:"))
        self.notification_interval = QSpinBox()
        self.notification_interval.setProperty("class", "iqama_input")
        self.notification_interval.setMinimum(1)
        self.notification_interval.setMaximum(10)
        self.notification_interval.setValue(self.notification_settings.get('notification_interval', 2))
        self.notification_interval.setSuffix(" min")
        self.notification_interval.setFixedWidth(100)
        settings_layout.addWidget(self.notification_interval)
        
        settings_layout.addStretch()
        sound_layout.addWidget(settings_row)
        layout.addWidget(sound_section)
        
        # Buttons section
        buttons_section = QWidget()
        buttons_section.setProperty("class", "settings_card")
        
        buttons_layout = QHBoxLayout(buttons_section)
        buttons_layout.setContentsMargins(20, 15, 20, 15)
        buttons_layout.setSpacing(15)
        
        # Test notification button
        test_btn = QPushButton("🔔 Test Notification")
        test_btn.setProperty("class", "modern_button")
        test_btn.clicked.connect(self.test_notification)
        test_btn.setCursor(Qt.PointingHandCursor)
        buttons_layout.addWidget(test_btn)
        
        # Reset button
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.setProperty("class", "cancel_button")
        reset_btn.clicked.connect(self.reset_notification_settings)
        reset_btn.setCursor(Qt.PointingHandCursor)
        buttons_layout.addWidget(reset_btn)
        
        layout.addWidget(buttons_section)
        layout.addStretch()
        
        return tab
    
    def load_notification_settings(self):
        """Load saved notification settings"""
        try:
            if os.path.exists(self.notifications_config_file):
                with open(self.notifications_config_file, 'r') as f:
                    settings = json.load(f)
                print(f"Loaded notification settings: {settings}")
                return settings
        except Exception as e:
            print(f"Could not load notification settings: {e}")
        print("Using default notification settings")
        return {}
    
    def save_notification_settings(self):
        """Save notification settings to config"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            notification_data = {
                'sound_enabled': self.sound_enabled.isChecked(),
                'snooze_duration': self.snooze_duration.value(),
                'notification_interval': self.notification_interval.value()
            }
            
            for prayer, inputs in self.notification_inputs.items():
                notification_data[prayer] = {
                    'enabled': inputs['enabled'].isChecked(),
                    'repeat_count': inputs['repeat_count'].value()
                }
            
            with open(self.notifications_config_file, 'w') as f:
                json.dump(notification_data, f, indent=2)
            
            print(f"Notification settings saved to: {self.notifications_config_file}")
            print(f"Settings: {notification_data}")
        except Exception as e:
            print(f"Could not save notification settings: {e}")
    
    def reset_notification_settings(self):
        """Reset all notification settings to defaults"""
        # Reset prayer notifications
        for prayer, inputs in self.notification_inputs.items():
            inputs['enabled'].setChecked(True)
            inputs['repeat_count'].setValue(3)
        
        # Reset sound settings
        self.sound_enabled.setChecked(True)
        self.snooze_duration.setValue(5)
        self.notification_interval.setValue(2)
    
    def test_notification(self):
        """Test the notification system"""
        try:
            import subprocess
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M")
            
            # Play sound FIRST if enabled
            if self.sound_enabled.isChecked():
                try:
                    subprocess.run(['paplay', '/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga'], 
                                 check=False, timeout=3)
                except:
                    try:
                        subprocess.run(['paplay', '/usr/share/sounds/freedesktop/stereo/message-new-instant.oga'], 
                                     check=False, timeout=3)
                    except:
                        print('\a')  # Fallback beep
            
            # Send test system notification with actions AFTER sound
            subprocess.Popen([
                'notify-send',
                '🔔 Test Prayer Time',
                f'This is a test notification\nTime: {current_time}\nSound: {"Enabled" if self.sound_enabled.isChecked() else "Disabled"}',
                '--urgency=critical',
                '--expire-time=0',  # Don't auto-expire for testing
                '--icon=appointment-soon',
                '--action=stop=⏹️ Stop'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        except Exception as e:
            QMessageBox.warning(self, "Test Failed", f"Could not test notification: {e}")
    
    def load_iqama_times(self):
        """Load saved Iqama times"""
        try:
            if os.path.exists(self.iqama_config_file):
                with open(self.iqama_config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Could not load Iqama times: {e}")
        return {}
    
    def save_iqama_times(self):
        """Save Iqama times to config"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            iqama_data = {}
            for prayer, input_widget in self.iqama_inputs.items():
                iqama_data[prayer] = input_widget.value()
            
            with open(self.iqama_config_file, 'w') as f:
                json.dump(iqama_data, f, indent=2)
        except Exception as e:
            print(f"Could not save Iqama times: {e}")
    
    def get_default_iqama(self, prayer):
        """Get default Iqama delay for prayer"""
        defaults = {'Fajr': 20, 'Dohr': 15, 'Asr': 15, 'Maghreb': 10, 'Isha': 15}
        return defaults.get(prayer, 15)
    
    def reset_iqama_times(self):
        """Reset all Iqama times to defaults"""
        for prayer, input_widget in self.iqama_inputs.items():
            input_widget.setValue(self.get_default_iqama(prayer))
    
    def restore_geometry(self):
        """Restore window geometry from saved settings"""
        try:
            if os.path.exists(self.geometry_file):
                with open(self.geometry_file, 'r') as f:
                    geometry = json.load(f)
                self.resize(geometry.get('width', 450), geometry.get('height', 550))
                if 'x' in geometry and 'y' in geometry:
                    self.move(geometry['x'], geometry['y'])
        except Exception as e:
            print(f"Could not restore settings geometry: {e}")
    
    def save_geometry(self):
        """Save current window geometry"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            geometry = {
                'width': self.width(),
                'height': self.height(),
                'x': self.x(),
                'y': self.y()
            }
            with open(self.geometry_file, 'w') as f:
                json.dump(geometry, f)
        except Exception as e:
            print(f"Could not save settings geometry: {e}")
    
    def accept(self):
        """Save settings when OK is clicked"""
        self.save_iqama_times()
        self.save_notification_settings()
        super().accept()
    
    def closeEvent(self, event):
        """Save geometry when dialog closes"""
        self.save_geometry()
        super().closeEvent(event)
        
    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)
    
    def tr_prayer(self, prayer_key):
        return TRANSLATIONS[self.current_language]['prayers'].get(prayer_key, prayer_key)
        
    def filter_cities(self, text):
        self.city_list.clear()
        translated_cities = self.get_translated_cities()
        filtered_cities = [city for city in translated_cities if text.lower() in city.lower()]
        self.city_list.addItems(filtered_cities)
        if filtered_cities:
            self.city_list.setCurrentRow(0)
        
    def get_translated_cities(self):
        return [CITIES[city][self.current_language] for city in self.cities]
        
    def get_city_key_from_translated(self, translated_name):
        for key, city_data in CITIES.items():
            if city_data[self.current_language] == translated_name:
                return key
        return translated_name
        
    def get_selected_city(self):
        current_item = self.city_list.currentItem()
        if current_item:
            translated_name = current_item.text()
            return self.get_city_key_from_translated(translated_name)
        return self.current_city
        
    def get_selected_language(self):
        lang_map = {0: 'en', 1: 'ar', 2: 'fr'}
        return lang_map.get(self.language_combo.currentIndex(), 'en')

class CitySelectionDialog(QDialog):
    def __init__(self, language='en', parent=None):
        super().__init__(parent)
        self.selected_city = None
        self.language = language
        self.cities = sorted(CITIES.keys())
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Welcome to Salah Times')
        self.setMinimumSize(450, 450)
        self.resize(450, 500)
        self.setModal(True)
        self.setStyleSheet(self.get_welcome_stylesheet())
        
        # Main container
        main_container = QWidget()
        main_container.setObjectName("welcome_main")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_container)
        
        layout = QVBoxLayout(main_container)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome header
        header = self.create_welcome_header()
        layout.addWidget(header, 0)
        
        # City selection card
        city_card = self.create_city_selection_card()
        layout.addWidget(city_card, 1)
        
        # Buttons
        buttons = self.create_welcome_buttons()
        layout.addWidget(buttons, 0)
    
    def get_welcome_stylesheet(self):
        return """
            #welcome_main {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fffe, stop:1 #e8f5e8);
            }
            
            .welcome_card {
                background: white;
                border-radius: 15px;
                border: 1px solid rgba(45, 90, 39, 0.1);
                padding: 25px;
            }
            
            .welcome_title {
                color: #2d5a27;
                font-size: 32px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            .welcome_subtitle {
                color: #666666;
                font-size: 16px;
                font-weight: 400;
                line-height: 1.4;
            }
            
            .welcome_search {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 15px;
                font-size: 14px;
                color: #333;
            }
            
            .welcome_search:focus {
                border-color: #2d5a27;
                outline: none;
            }
            
            .welcome_list {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                font-size: 14px;
                color: #333;
                outline: none;
            }
            
            .welcome_list::item {
                padding: 15px;
                border-bottom: 1px solid #f0f0f0;
            }
            
            .welcome_list::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a7c59, stop:1 #2d5a27);
                color: white;
            }
            
            .welcome_list::item:hover {
                background: rgba(45, 90, 39, 0.1);
            }
            
            .welcome_button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4a7c59, stop:1 #2d5a27);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 16px 32px;
                font-size: 16px;
                font-weight: 600;
            }
            
            .welcome_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a8c69, stop:1 #3d6a37);
            }
            
            .welcome_cancel {
                background: #f5f5f5;
                color: #666;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 16px 32px;
                font-size: 16px;
                font-weight: 600;
            }
            
            .welcome_cancel:hover {
                background: #e8e8e8;
                border-color: #ccc;
            }
        """
    
    def create_welcome_header(self):
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        title = QLabel(self.tr('welcome'))
        title.setProperty("class", "welcome_title")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)
        
        subtitle = QLabel(self.tr('select_city'))
        subtitle.setProperty("class", "welcome_subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        return header
    
    def create_city_selection_card(self):
        card = QWidget()
        card.setProperty("class", "welcome_card")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setProperty("class", "welcome_search")
        self.search_box.setPlaceholderText(self.tr('search_city'))
        self.search_box.textChanged.connect(self.filter_cities)
        layout.addWidget(self.search_box)
        
        # City list
        self.city_list = QListWidget()
        self.city_list.setProperty("class", "welcome_list")
        translated_cities = self.get_translated_cities()
        self.city_list.addItems(translated_cities)
        tangier_translated = CITIES['Tangier'][self.language]
        try:
            self.city_list.setCurrentRow(translated_cities.index(tangier_translated))
        except ValueError:
            self.city_list.setCurrentRow(0)
        layout.addWidget(self.city_list, 1)
        
        return card
    
    def create_welcome_buttons(self):
        section = QWidget()
        layout = QHBoxLayout(section)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        cancel_btn = QPushButton(self.tr('cancel'))
        cancel_btn.setProperty("class", "welcome_cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton(self.tr('set_default'))
        ok_btn.setProperty("class", "welcome_button")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(ok_btn)
        
        return section
        
    def filter_cities(self, text):
        self.city_list.clear()
        translated_cities = self.get_translated_cities()
        filtered_cities = [city for city in translated_cities if text.lower() in city.lower()]
        self.city_list.addItems(filtered_cities)
        if filtered_cities:
            self.city_list.setCurrentRow(0)
        
    def tr(self, key):
        return TRANSLATIONS[self.language].get(key, key)
        
    def get_translated_cities(self):
        return [CITIES[city][self.language] for city in self.cities]
        
    def get_city_key_from_translated(self, translated_name):
        for key, city_data in CITIES.items():
            if city_data[self.language] == translated_name:
                return key
        return translated_name
        
    def get_selected_city(self):
        current_item = self.city_list.currentItem()
        if current_item:
            translated_name = current_item.text()
            return self.get_city_key_from_translated(translated_name)
        return 'Tangier'
