import os
import json
import threading
import requests
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .constants import TRANSLATIONS, CITIES, CITY_SLUGS
from .database import check_internet, update_all_cities, reset_day_counter, get_db_info
from .worker import PrayerTimeWorker
from .dialogs import SettingsDialog, CitySelectionDialog
try:
    from .views import MonthlyCalendarDialog, WeeklyScheduleDialog, TimezoneViewDialog
except ImportError:
    MonthlyCalendarDialog = WeeklyScheduleDialog = TimezoneViewDialog = None

class ModernSalahApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.prayer_times = {}
        self.current_prayer = None
        self.is_offline = False
        self.days_remaining = 0
        self.config_dir = os.path.join(os.path.expanduser('~'), '.salah_times', 'config')
        self.config_file = os.path.join(self.config_dir, 'app_config.json')
        self.geometry_file = os.path.join(self.config_dir, 'main_geometry.json')
        self.iqama_config_file = os.path.join(self.config_dir, 'iqama_times.json')
        self.notifications_config_file = os.path.join(self.config_dir, 'notifications.json')
        self.ensure_iqama_config_exists()
        self.ensure_notifications_config_exists()
        self.current_language = self.load_language_config()
        self.current_city = self.load_city_config()
        self.tray_icon = None
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # Update every second
        
        self.init_ui()
        self.restore_geometry()
        self.update_all_ui_text()
        self.load_prayer_times()
        # Start tray indicator with delay to ensure main app is ready
        QTimer.singleShot(2000, self.start_tray_indicator)
        
    def load_language_config(self):
        os.makedirs(self.config_dir, exist_ok=True)
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('language', 'en')
            except:
                pass
        return 'en'
    
    def load_city_config(self):
        os.makedirs(self.config_dir, exist_ok=True)
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('city', 'Tangier')
            except:
                pass
        
        # First time - show city selection
        dialog = CitySelectionDialog(self.current_language)
        if dialog.exec_() == QDialog.Accepted:
            city = dialog.get_selected_city()
            self.save_config(city, self.current_language)
            return city
        else:
            return 'Tangier'  # Default fallback
    
    def save_config(self, city, language):
        config = {'city': city, 'language': language}
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass
    
    def show_settings(self):
        dialog = SettingsDialog(self.current_city, self.current_language)
        
        if dialog.exec_() == QDialog.Accepted:
            new_city = dialog.get_selected_city()
            new_language = dialog.get_selected_language()
            
            if new_city != self.current_city or new_language != self.current_language:
                old_city = self.current_city
                self.current_city = new_city
                self.current_language = new_language
                self.save_config(new_city, new_language)
                self.update_ui_language()
                if new_city != old_city:
                    self.prayer_times = {}
                    self.load_prayer_times()
                if self.tray_icon:
                    self.create_tray_menu()
                    self.update_tray_tooltip()
        
    def init_ui(self):
        self.setWindowTitle('Salah Times')
        self.setMinimumSize(400, 600)
        self.resize(480, 720)
        self.setStyleSheet(self.get_modern_stylesheet())
        
        # Create menu bar
        self.create_menu_bar()
        
        # Default center position (will be overridden by restore_geometry if saved)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.default_x = (screen.width() - size.width()) // 2
        self.default_y = (screen.height() - size.height()) // 2
        
        # Main widget with gradient background
        main_widget = QWidget()
        main_widget.setObjectName("main_container")
        self.setCentralWidget(main_widget)
        
        # Main layout
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Top bar with title and settings (fixed size)
        top_bar = self.create_top_bar()
        layout.addWidget(top_bar, 0)  # No stretch
        
        # Current time and location card
        time_location_card = self.create_time_location_card()
        layout.addWidget(time_location_card, 1)  # Equal stretch
        
        # Prayer times grid
        prayer_grid = self.create_prayer_grid()
        layout.addWidget(prayer_grid, 2)  # Double stretch (main content)
        
        # Next prayer highlight
        next_prayer_highlight = self.create_next_prayer_highlight()
        layout.addWidget(next_prayer_highlight, 1)  # Equal stretch
        
        # Bottom controls (fixed size)
        bottom_controls = self.create_bottom_controls()
        layout.addWidget(bottom_controls, 0)  # No stretch
        
    def get_modern_stylesheet(self):
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fffe, stop:1 #e8f5e8);
            }
            
            #main_container {
                background: transparent;
            }
            
            .glass_card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d5a27, stop:1 #4a7c59);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
            }
            
            .prayer_card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: none;
                margin: 5px;
            }
            
            .prayer_card_current {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 15px;
                border: none;
                margin: 5px;
            }
            
            .prayer_row {
                background: transparent;
                border-radius: 8px;
            }
            
            .prayer_row:hover {
                background: rgba(45, 90, 39, 0.06);
                border-radius: 8px;
            }
            
            .prayer_card QLabel {
                color: #2c3e50;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }
            
            .prayer_card_current QLabel {
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }
            
            .prayer_icon {
                font-size: 28px;
                font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", Arial;
            }
            
            .prayer_name {
                font-size: 22px;
                font-weight: 600;
            }
            
            .prayer_time {
                font-size: 22px;
                font-weight: bold;
            }
            
            .title_text {
                color: #2d5a27;
                font-size: 28px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            .subtitle_text {
                color: #666666;
                font-size: 14px;
                font-weight: 400;
            }
            
            .time_text {
                color: white;
                font-size: 48px;
                font-weight: 100;
                font-family: 'Segoe UI Light', Arial, sans-serif;
            }
            
            .date_text {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                font-weight: 400;
            }
            
            .next_prayer_highlight {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4a7c59, stop:1 #2d5a27);
                border-radius: 20px;
                border: none;
            }
            
            .next_prayer_text {
                color: white;
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .next_prayer_name {
                color: white;
                font-size: 24px;
                font-weight: 600;
            }
            
            .countdown_text {
                color: white;
                font-size: 36px;
                font-weight: 100;
                font-family: 'Segoe UI Light', Arial, sans-serif;
            }
            
            .modern_button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4a7c59, stop:1 #2d5a27);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 14px;
                font-weight: 500;
                padding: 12px 24px;
            }
            
            .modern_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a8c69, stop:1 #3d6a37);
            }
            
            .modern_button:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1d4a17, stop:1 #2d5a27);
            }
            
            .settings_button {
                background: rgba(45, 90, 39, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 20px;
                color: white;
                font-size: 18px;
                padding: 10px;
            }
            
            .settings_button:hover {
                background: rgba(45, 90, 39, 1.0);
            }
            
            .iqama_text {
                color: #FFD700;
                font-size: 14px;
                font-weight: 500;
            }
        """
        
    def create_top_bar(self):
        top_bar = QWidget()
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title section
        title_section = QWidget()
        title_layout = QVBoxLayout(title_section)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        
        self.title_label = QLabel()
        self.title_label.setProperty("class", "title_text")
        title_layout.addWidget(self.title_label)
        
        self.location_label = QLabel()
        self.location_label.setProperty("class", "subtitle_text")
        title_layout.addWidget(self.location_label)
        
        # Offline indicator
        self.offline_indicator = QLabel("")
        self.offline_indicator.setStyleSheet("color: #FFD700; font-size: 12px; font-weight: 500;")
        title_layout.addWidget(self.offline_indicator)
        
        layout.addWidget(title_section)
        layout.addStretch()
        
        # Settings button
        settings_btn = QPushButton("⚙️")
        settings_btn.setProperty("class", "settings_button")
        settings_btn.clicked.connect(self.show_settings)
        settings_btn.setMinimumSize(35, 35)
        settings_btn.setMaximumSize(50, 50)
        settings_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(settings_btn)
        
        return top_bar
    
    def create_time_location_card(self):
        card = QWidget()
        card.setProperty("class", "glass_card")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Current time
        current_time = datetime.now().strftime("%H:%M")
        time_label = QLabel(current_time)
        time_label.setProperty("class", "time_text")
        time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(time_label, 1)
        
        # Date info container
        date_container = QWidget()
        date_layout = QVBoxLayout(date_container)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(4)
        
        self.current_date = QLabel()
        self.current_date.setProperty("class", "date_text")
        self.current_date.setAlignment(Qt.AlignCenter)
        self.current_date.setWordWrap(True)
        date_layout.addWidget(self.current_date)
        
        self.hijri_date = QLabel()
        self.hijri_date.setProperty("class", "date_text")
        self.hijri_date.setAlignment(Qt.AlignCenter)
        self.hijri_date.setWordWrap(True)
        date_layout.addWidget(self.hijri_date)
        
        layout.addWidget(date_container, 0)
        
        return card
    
    def create_prayer_grid(self):
        container = QWidget()
        container.setProperty("class", "prayer_card")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(0)
        
        self.prayer_cards = {}
        prayers = ['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha']
        icons = {'Fajr': '☽', 'Dohr': '☉', 'Asr': '☀', 'Maghreb': '☾', 'Isha': '★'}
        
        for i, prayer in enumerate(prayers):
            row = self.create_prayer_card_widget(prayer, icons[prayer], '--:--')
            row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(row, 1)
            self.prayer_cards[prayer] = row
            if i < len(prayers) - 1:
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet("color: rgba(0,0,0,0.08); margin: 0px 4px;")
                layout.addWidget(sep)
        
        return container
    
    def create_prayer_card_widget(self, prayer_name, icon, time, is_current=False, inline=False):
        card = QWidget()
        card.setProperty("class", "prayer_card_current" if is_current else "prayer_row")
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(0)
        
        icon_label = QLabel(icon)
        icon_label.setFixedWidth(40)
        icon_label.setStyleSheet("font-size: 26px;")
        layout.addWidget(icon_label)
        
        name_label = QLabel(self.tr_prayer(prayer_name))
        name_label.setProperty("class", "prayer_name")
        name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(name_label)
        
        dash = QLabel("—")
        dash.setStyleSheet("color: #aaa; font-size: 14px; padding: 0 8px;")
        dash.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        layout.addWidget(dash)
        
        time_label = QLabel(time)
        time_label.setProperty("class", "prayer_time")
        time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        time_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(time_label)
        
        return card
    
    def create_next_prayer_highlight(self):
        card = QWidget()
        card.setProperty("class", "next_prayer_highlight")
        card.setMinimumHeight(80)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setAlignment(Qt.AlignCenter)
        
        # Next prayer label
        self.next_label = QLabel()
        self.next_label.setProperty("class", "next_prayer_text")
        self.next_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.next_label)
        
        # Prayer name and time
        info_layout = QHBoxLayout()
        
        prayer_info_layout = QVBoxLayout()
        
        self.next_name = QLabel("")
        self.next_name.setProperty("class", "next_prayer_name")
        self.next_name.setWordWrap(True)
        prayer_info_layout.addWidget(self.next_name)
        
        self.next_time = QLabel("")
        self.next_time.setProperty("class", "subtitle_text")
        self.next_time.setWordWrap(True)
        prayer_info_layout.addWidget(self.next_time)
        
        info_layout.addLayout(prayer_info_layout)
        info_layout.addStretch()
        
        self.countdown = QLabel("")
        self.countdown.setProperty("class", "countdown_text")
        self.countdown.setWordWrap(True)
        info_layout.addWidget(self.countdown)
        
        layout.addLayout(info_layout)
        
        # Iqama countdown
        self.iqama_countdown = QLabel("")
        self.iqama_countdown.setProperty("class", "iqama_text")
        self.iqama_countdown.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.iqama_countdown)
        
        return card
    
    def create_bottom_controls(self):
        controls = QWidget()
        layout = QHBoxLayout(controls)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(10)
        
        # Refresh today button
        self.refresh_btn = QPushButton()
        self.refresh_btn.setProperty("class", "modern_button")
        self.refresh_btn.clicked.connect(self.load_prayer_times)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.refresh_btn)
        
        # Refresh full database button
        self.refresh_db_btn = QPushButton(self.tr('refresh_db'))
        self.refresh_db_btn.setProperty("class", "modern_button")
        self.refresh_db_btn.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #7c4a4a,stop:1 #5a2727);")
        self.refresh_db_btn.clicked.connect(self.refresh_full_database)
        self.refresh_db_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.refresh_db_btn)
        
        return controls
    
    def refresh_full_database(self):
        self.refresh_db_btn.setText(self.tr('refresh_db_updating'))
        self.refresh_db_btn.setEnabled(False)
        
        self.db_worker = PrayerTimeWorker(self.current_city)
        
        no_internet_result = []
        
        def run_full_update():
            if not check_internet():
                no_internet_result.append(True)
                return
            try:
                update_all_cities()
                reset_day_counter()
            except Exception as e:
                print(f"Full DB update error: {e}")
        
        def on_done():
            self.refresh_db_btn.setText(self.tr('refresh_db'))
            self.refresh_db_btn.setEnabled(True)
            if no_internet_result:
                info = get_db_info()
                QMessageBox.warning(
                    self,
                    self.tr('no_internet_title'),
                    self.tr('no_internet_msg').format(
                        info['cities'], info['first_date'], info['last_date']
                    )
                )
            else:
                self.load_prayer_times()
        
        t = threading.Thread(target=run_full_update, daemon=True)
        t.start()
        
        def check_done():
            if t.is_alive():
                QTimer.singleShot(500, check_done)
            else:
                on_done()
        
        QTimer.singleShot(500, check_done)
    
    def get_db_info(self):
        db_path = os.path.join(os.path.expanduser('~'), '.salah_times', 'salah.db')
        result = {'cities': 0, 'first_date': 'N/A', 'last_date': 'N/A'}
        if not os.path.exists(db_path):
            return result
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]
            result['cities'] = len(tables)
            if tables:
                cursor.execute(f'SELECT date FROM {tables[0]} ORDER BY rowid ASC LIMIT 1')
                first = cursor.fetchone()
                cursor.execute(f'SELECT date FROM {tables[0]} ORDER BY rowid DESC LIMIT 1')
                last = cursor.fetchone()
                if first:
                    result['first_date'] = first[0]
                if last:
                    result['last_date'] = last[0]
            conn.close()
        except Exception as e:
            print(f"DB info error: {e}")
        return result
    def prompt_db_refresh(self):
        reply = QMessageBox.question(
            self,
            self.tr('refresh_db_prompt_title'),
            self.tr('refresh_db_prompt_msg'),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.refresh_full_database()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background: #2d5a27;
                color: white;
                border: none;
                padding: 5px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: rgba(255, 255, 255, 0.2);
            }
            QMenu {
                background: #2d5a27;
                color: white;
                border: 1px solid #4a7c59;
                border-radius: 6px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #4a7c59;
            }
        """)
        
        # View menu
        view_menu = menubar.addMenu(self.tr('view'))
        
        # Monthly calendar action
        monthly_action = QAction(f"📅 {self.tr('monthly_calendar')}", self)
        monthly_action.triggered.connect(self.show_monthly_calendar)
        view_menu.addAction(monthly_action)
        
        # Weekly schedule action
        weekly_action = QAction(f"📋 {self.tr('weekly_schedule')}", self)
        weekly_action.triggered.connect(self.show_weekly_schedule)
        view_menu.addAction(weekly_action)
        
        # Timezone view action
        timezone_action = QAction(f"🌍 {self.tr('timezone_view')}", self)
        timezone_action.triggered.connect(self.show_timezone_view)
        view_menu.addAction(timezone_action)
    
    def show_monthly_calendar(self):
        if MonthlyCalendarDialog:
            dialog = MonthlyCalendarDialog(self.current_city, self.current_language, self)
            dialog.exec_()
        else:
            QMessageBox.information(self, "Feature Unavailable", "Monthly calendar feature is not available.")
    
    def show_weekly_schedule(self):
        if WeeklyScheduleDialog:
            dialog = WeeklyScheduleDialog(self.current_city, self.current_language, self)
            dialog.exec_()
        else:
            QMessageBox.information(self, "Feature Unavailable", "Weekly schedule feature is not available.")
    
    def show_timezone_view(self):
        if TimezoneViewDialog:
            dialog = TimezoneViewDialog(self.current_city, self.current_language, self)
            dialog.exec_()
        else:
            QMessageBox.information(self, "Feature Unavailable", "Timezone view feature is not available.")
        
    def create_date_card_old(self):
        card = QWidget()
        card.setObjectName("date_card")
        card.setProperty("class", "date_card")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)
        
        # Hijri date first (more important)
        self.hijri_date = QLabel()
        self.hijri_date.setObjectName("hijri_date")
        self.hijri_date.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.hijri_date)
        
        # Gregorian date second
        self.current_date = QLabel()
        self.current_date.setObjectName("current_date")
        self.current_date.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.current_date)
        
        return card
        
    def create_prayer_card(self):
        card = QWidget()
        card.setProperty("class", "card")
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 8px; background: #f0f0f0; border-radius: 4px; } QScrollBar::handle:vertical { background: #c0c0c0; border-radius: 4px; } QScrollBar::handle:vertical:hover { background: #a0a0a0; }")
        
        scroll_widget = QWidget()
        self.prayer_layout = QVBoxLayout(scroll_widget)
        self.prayer_layout.setContentsMargins(15, 15, 15, 15)
        self.prayer_layout.setSpacing(0)
        self.prayer_layout.addStretch()
        
        loading = QLabel("🔄 Loading prayer times...")
        loading.setProperty("class", "loading")
        loading.setAlignment(Qt.AlignCenter)
        self.prayer_layout.addWidget(loading)
        
        scroll_area.setWidget(scroll_widget)
        card_layout.addWidget(scroll_area)
        
        return card
        
    def create_next_prayer_card(self):
        card = QWidget()
        card.setProperty("class", "next_prayer_card")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        self.next_label = QLabel()
        self.next_label.setObjectName("next_label")
        self.next_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.next_label)
        
        self.next_name = QLabel("")
        self.next_name.setObjectName("next_name")
        self.next_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.next_name)
        
        self.next_time = QLabel("")
        self.next_time.setObjectName("next_time")
        self.next_time.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.next_time)
        
        self.countdown = QLabel("")
        self.countdown.setObjectName("countdown")
        self.countdown.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.countdown)
        
        self.iqama_countdown = QLabel("")
        self.iqama_countdown.setObjectName("iqama_countdown")
        self.iqama_countdown.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.iqama_countdown)
        
        return card
        
    def create_refresh_button(self):
        self.refresh_btn = QPushButton()
        self.refresh_btn.setObjectName("refresh_btn")
        self.refresh_btn.clicked.connect(self.load_prayer_times)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        return self.refresh_btn
        
    def fetch_hijri_date(self):
        try:
            today = datetime.now().strftime("%d-%m-%Y")
            url = f"http://api.aladhan.com/v1/gToH/{today}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data['code'] == 200:
                hijri = data['data']['hijri']
                if self.current_language == 'ar':
                    # Use Arabic month name from API
                    month_ar = hijri['month']['ar']
                    hijri_text = f"{hijri['day']} {month_ar} {hijri['year']} هـ"
                else:
                    # Use English month name from API
                    month_en = hijri['month']['en']
                    hijri_text = f"{hijri['day']} {month_en} {hijri['year']} AH"
                self.hijri_date.setText(hijri_text)
            else:
                self.hijri_date.setText(self.tr('hijri_unavailable'))
        except:
            hijri_year = int((datetime.now().year - 622) * 1.030684)
            self.hijri_date.setText(self.tr('hijri_approx').format(hijri_year))
    
    def load_prayer_times(self):
        # Show loading state in prayer cards
        for prayer in ['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha']:
            if hasattr(self, 'prayer_cards') and prayer in self.prayer_cards:
                # Update card to show loading
                card = self.prayer_cards[prayer]
                # Find the time label and update it
                for child in card.findChildren(QLabel):
                    if child.property("class") == "prayer_time":
                        child.setText("...")
        
        # Reset offline status
        self.is_offline = False
        self.days_remaining = 0
        self.update_offline_indicator()
        
        # Update refresh button text
        if hasattr(self, 'refresh_btn'):
            self.refresh_btn.setText("🔄 Loading...")
        
        # Start worker thread
        self.worker = PrayerTimeWorker(self.current_city)
        self.worker.data_received.connect(self.display_prayer_times)
        self.worker.offline_data_loaded.connect(self.display_offline_prayer_times)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.db_refresh_needed.connect(self.prompt_db_refresh)
        self.worker.start()
        
    def clear_prayer_layout(self):
        # Not needed with new grid system
        pass
                
    def display_prayer_times(self, prayer_times):
        self.prayer_times = prayer_times
        self.is_offline = False
        self.update_offline_indicator()
        self._display_prayer_times_common(prayer_times)
    
    def display_offline_prayer_times(self, prayer_times, days_remaining):
        self.prayer_times = prayer_times
        self.is_offline = True
        self.days_remaining = days_remaining
        self.update_offline_indicator()
        self._display_prayer_times_common(prayer_times)
    
    def _display_prayer_times_common(self, prayer_times):
        current_prayer = self.get_current_prayer()
        
        display_times = {k: v for k, v in prayer_times.items() if k != 'Date'}
        
        # Update prayer cards with new times and styling
        for prayer, time in display_times.items():
            if prayer in self.prayer_cards and prayer != 'Date':
                card = self.prayer_cards[prayer]
                is_current = (prayer == current_prayer)
                
                card.setProperty("class", "prayer_card_current" if is_current else "prayer_row")
                card.style().unpolish(card)
                card.style().polish(card)
                
                for child in card.findChildren(QLabel):
                    if child.property("class") == "prayer_name":
                        child.setText(self.tr_prayer(prayer))
                        child.setStyleSheet("color: white; font-weight: 700; font-size: 22px;" if is_current else "font-size: 22px;")
                    elif child.property("class") == "prayer_time":
                        child.setText(time)
                        child.setStyleSheet("color: white; font-weight: 700; font-size: 22px;" if is_current else "font-size: 22px;")
        
        # Update refresh button
        if hasattr(self, 'refresh_btn'):
            self.refresh_btn.setText(self.tr('refresh'))
        
        self.update_next_prayer()
        self.update_countdown()
        
        # Update tray tooltip if it exists
        if self.tray_icon:
            self.update_tray_tooltip()
        
        # Update tray if it exists
        if self.tray_icon:
            self.create_tray_menu()
            self.update_tray_tooltip()
    
    def update_offline_indicator(self):
        if self.is_offline:
            if self.days_remaining > 0:
                self.offline_indicator.setText(f"📶 Offline - {self.days_remaining} days left")
            else:
                self.offline_indicator.setText("📶 Offline - Data expired")
        else:
            self.offline_indicator.setText("")
    
    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)
    
    def tr_prayer(self, prayer_key):
        return TRANSLATIONS[self.current_language]['prayers'].get(prayer_key, prayer_key)
    
    def tr_city(self, city_key):
        return CITIES[city_key][self.current_language]
    
    def get_translated_date(self):
        now = datetime.now()
        day_name = self.tr('days')[now.weekday()]
        month_name = self.tr('months')[now.month - 1]
        return f"{day_name}, {month_name} {now.day}, {now.year}"
    
    def update_dates(self):
        self.current_date.setText(self.get_translated_date())
        self.fetch_hijri_date()
    
    def update_location_label(self):
        translated_city = self.tr_city(self.current_city)
        self.location_label.setText(f"{translated_city}, {self.tr('morocco')}")
    
    def update_all_ui_text(self):
        translated_city = self.tr_city(self.current_city)
        self.setWindowTitle(f'🕌 {self.tr("app_title")} - {translated_city}')
        self.title_label.setText(self.tr('app_title'))
        self.next_label.setText(self.tr('next_prayer'))
        self.refresh_btn.setText(self.tr('refresh'))
        if hasattr(self, 'refresh_db_btn') and self.refresh_db_btn.isEnabled():
            self.refresh_db_btn.setText(self.tr('refresh_db'))
        self.update_location_label()
        self.update_dates()
    
    def update_ui_language(self):
        self.update_all_ui_text()
        # Refresh menu bar
        self.menuBar().clear()
        self.create_menu_bar()
        # Refresh prayer times display to update translations
        if self.prayer_times:
            self.display_prayer_times(self.prayer_times)
        
    def get_current_prayer(self):
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
        
    def parse_time(self, time_str):
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except:
            return 0
            
    def update_next_prayer(self):
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        
        prayers = [name for name in self.prayer_times.keys() if name != 'Date']
        
        for prayer in prayers:
            if prayer in self.prayer_times:
                prayer_time = self.parse_time(self.prayer_times[prayer])
                if prayer_time > current_time:
                    self.next_name.setText(self.tr_prayer(prayer))
                    self.next_time.setText(self.prayer_times[prayer])
                    return
        
        if prayers and prayers[0] in self.prayer_times:
            first_prayer = prayers[0]
            self.next_name.setText(f"{self.tr_prayer(first_prayer)} ({self.tr('tomorrow')})")
            self.next_time.setText(self.prayer_times[first_prayer])
            
    def ensure_iqama_config_exists(self):
        """Create Iqama config with defaults if it doesn't exist"""
        if not os.path.exists(self.iqama_config_file):
            try:
                os.makedirs(self.config_dir, exist_ok=True)
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
                os.makedirs(self.config_dir, exist_ok=True)
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
    
    def get_iqama_delay(self, prayer):
        """Get Iqama delay from config"""
        iqama_times = self.load_iqama_times()
        return iqama_times.get(prayer, 15)
    
    def is_iqama_time(self, prayer):
        if not prayer or prayer not in self.prayer_times:
            return False
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        prayer_time = self.parse_time(self.prayer_times[prayer])
        iqama_delay = self.get_iqama_delay(prayer)
        
        return prayer_time <= current_time < prayer_time + iqama_delay
    
    def _gtk_menu_item(self, label, callback=None, sensitive=True):
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        item = Gtk.MenuItem(label=label)
        item.set_sensitive(sensitive)
        if callback:
            item.connect('activate', lambda w: callback())
        item.show()
        return item

    def create_tray_menu(self):
        """Create Gtk menu for GNOME AppIndicator"""
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk

        menu = Gtk.Menu()
        city_name = self.tr_city(self.current_city)
        menu.append(self._gtk_menu_item(f"🕌 Salah Times - {city_name}", callback=self.show_and_raise))
        menu.append(Gtk.SeparatorMenuItem.new())

        if self.prayer_times:
            icons = {'Fajr': '☽', 'Dohr': '☉', 'Asr': '☀', 'Maghreb': '☾', 'Isha': '★'}
            current_prayer = self.get_current_prayer()
            for prayer in ['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha']:
                if prayer not in self.prayer_times:
                    continue
                t = self.prayer_times[prayer]
                icon = icons.get(prayer, '🕐')
                name = self.tr_prayer(prayer)
                marker = ' ◄' if prayer == current_prayer else ''
                menu.append(self._gtk_menu_item(f"{icon} {name}: {t}{marker}", callback=self.show_and_raise))
        else:
            menu.append(self._gtk_menu_item("🔄 Loading prayer times...", sensitive=False))

        menu.append(Gtk.SeparatorMenuItem.new())
        next_prayer = self.get_next_prayer()
        if next_prayer and self.prayer_times:
            name = self.tr_prayer(next_prayer)
            t = self.prayer_times.get(next_prayer, '--:--')
            menu.append(self._gtk_menu_item(f"⏰ {self.tr('next_prayer')}: {name} {t}", callback=self.show_and_raise))

        menu.append(self._gtk_menu_item(f"📅 {self.get_translated_date()}", callback=self.show_and_raise))
        menu.append(Gtk.SeparatorMenuItem.new())
        menu.append(self._gtk_menu_item(self.tr('tray_show'), callback=self.show_and_raise))
        menu.append(self._gtk_menu_item(self.tr('tray_refresh'), callback=self.load_prayer_times))
        menu.append(Gtk.SeparatorMenuItem.new())
        menu.append(self._gtk_menu_item(self.tr('tray_quit'), callback=self.cleanup_and_quit))
        menu.show_all()
        self.tray_icon.set_menu(menu)
    
    def get_countdown_to_next_prayer(self):
        """Get countdown to next prayer"""
        if not self.prayer_times:
            return "00:00:00"

        now = datetime.now()
        now_secs = now.hour * 3600 + now.minute * 60 + now.second

        prayers = ['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha']

        for prayer in prayers:
            if prayer not in self.prayer_times:
                continue
            prayer_secs = self.parse_time(self.prayer_times[prayer]) * 60

            if prayer_secs > now_secs:
                remaining = prayer_secs - now_secs
                h = remaining // 3600
                m = (remaining % 3600) // 60
                s = remaining % 60
                return f"{h:02d}:{m:02d}:{s:02d}"

        if 'Fajr' in self.prayer_times:
            fajr_secs = self.parse_time(self.prayer_times['Fajr']) * 60
            remaining = 86400 - now_secs + fajr_secs
            h = remaining // 3600
            m = (remaining % 3600) // 60
            s = remaining % 60
            return f"{h:02d}:{m:02d}:{s:02d}"

        return "00:00:00"
    
    def get_next_prayer(self):
        """Get next prayer name"""
        if not self.prayer_times:
            return None
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        
        prayers = ['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha']
        
        for prayer in prayers:
            if prayer not in self.prayer_times:
                continue
            prayer_time = self.parse_time(self.prayer_times[prayer])
            
            if prayer_time > current_time:
                return prayer
        
        # If no prayer today, return Fajr for tomorrow
        return 'Fajr'
    
    def update_tray_tooltip(self):
        if not self.tray_icon:
            return
        next_prayer = self.get_next_prayer()
        if next_prayer:
            name = self.tr_prayer(next_prayer)
            t = self.prayer_times.get(next_prayer, '--:--')
            countdown = self.get_countdown_to_next_prayer()
            label = f"{name} {t} {countdown}"
        else:
            label = "--"
        self.tray_icon.set_label(label, "")
    
    def update_countdown(self):
        if not self.prayer_times:
            return

        now = datetime.now()
        current_seconds = now.second

        # Recalculate remaining minutes only once per minute (when seconds == 0)
        # or on first call (when _countdown_remaining is not set)
        if current_seconds == 0 or not hasattr(self, '_countdown_remaining'):
            current_time = now.hour * 60 + now.minute
            prayers = [name for name in self.prayer_times.keys() if name != 'Date']

            # Iqama: current prayer and remaining minutes
            current_prayer = self.get_current_prayer()
            if current_prayer:
                prayer_time = self.parse_time(self.prayer_times[current_prayer])
                iqama_end_time = prayer_time + self.get_iqama_delay(current_prayer)
                self._iqama_remaining = iqama_end_time - current_time
                self._iqama_prayer = current_prayer
            else:
                self._iqama_remaining = -1
                self._iqama_prayer = None

            # Next prayer remaining minutes
            next_prayer_time = None
            for prayer in prayers:
                if prayer in self.prayer_times:
                    t = self.parse_time(self.prayer_times[prayer])
                    if t > current_time:
                        next_prayer_time = t
                        break
            if next_prayer_time is not None:
                self._countdown_remaining = next_prayer_time - current_time
            elif 'Fajr' in self.prayer_times:
                self._countdown_remaining = (24 * 60) + self.parse_time(self.prayer_times['Fajr']) - current_time
            else:
                self._countdown_remaining = 0

        # Every second: just subtract elapsed seconds from cached remaining minutes
        iqama_remaining = getattr(self, '_iqama_remaining', -1)
        iqama_prayer = getattr(self, '_iqama_prayer', None)
        remaining = getattr(self, '_countdown_remaining', 0)

        # Convert remaining minutes to H:M:S using current_seconds offset
        def to_hms(total_minutes):
            total_secs = total_minutes * 60 - current_seconds
            if total_secs < 0:
                total_secs = 0
            h = total_secs // 3600
            m = (total_secs % 3600) // 60
            s = total_secs % 60
            return h, m, s

        if iqama_prayer:
            if iqama_remaining <= 0:
                self.iqama_countdown.setText(self.tr('iqama_passed').format(self.tr_prayer(iqama_prayer)))
                self.iqama_countdown.setStyleSheet("color: #90EE90; font-weight: bold;")
            else:
                h, m, s = to_hms(iqama_remaining)
                self.iqama_countdown.setText(self.tr('iqama_time').format(self.tr_prayer(iqama_prayer), h, m, s))
                self.iqama_countdown.setStyleSheet("color: #90EE90; font-weight: bold;")
        else:
            self.iqama_countdown.setText("")

        if remaining > 0:
            h, m, s = to_hms(remaining)
            self.countdown.setText(f"{h:02d}:{m:02d}:{s:02d}")
            
    def show_error(self, error_message):
        # Show error in prayer cards
        for prayer in ['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha']:
            if hasattr(self, 'prayer_cards') and prayer in self.prayer_cards:
                card = self.prayer_cards[prayer]
                for child in card.findChildren(QLabel):
                    if child.property("class") == "prayer_time":
                        child.setText("Error")
                        child.setStyleSheet("color: #ff4444;")
    
    def start_tray_indicator(self):
        """Create AppIndicator tray icon (GNOME compatible)"""
        try:
            if self.tray_icon is not None:
                return

            # Block GTK from loading snap modules that cause pthread conflicts
            os.environ['GTK_MODULES'] = ''
            os.environ['GTK2_RC_FILES'] = ''

            import gi
            gi.require_version('AyatanaAppIndicator3', '0.1')
            gi.require_version('Gtk', '3.0')
            from gi.repository import AyatanaAppIndicator3, Gtk
            import threading

            self.tray_icon = AyatanaAppIndicator3.Indicator.new(
                "salah-times",
                "appointment-soon",
                AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.tray_icon.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
            self.tray_icon.set_label("--:--:--", "")

            self.create_tray_menu()

            self._gtk_thread = threading.Thread(target=Gtk.main, daemon=True)
            self._gtk_thread.start()

            self.tray_timer = QTimer()
            self.tray_timer.timeout.connect(self.update_tray_display)
            self.tray_timer.start(1000)

            print("AppIndicator tray started")
        except Exception as e:
            print(f"Could not create AppIndicator tray: {e}")
            import traceback
            traceback.print_exc()
    
    def update_tray_display(self):
        if not self.tray_icon:
            return
        self.update_tray_tooltip()
        if not hasattr(self, '_menu_tick'):
            self._menu_tick = 0
        self._menu_tick += 1
        if self._menu_tick >= 60:
            self._menu_tick = 0
            self.create_tray_menu()
    
    def show_and_raise(self):
        """Show and raise the main window"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def restore_geometry(self):
        """Restore window geometry from saved settings"""
        try:
            if os.path.exists(self.geometry_file):
                with open(self.geometry_file, 'r') as f:
                    geometry = json.load(f)
                self.resize(geometry.get('width', 480), geometry.get('height', 720))
                if 'x' in geometry and 'y' in geometry:
                    self.move(geometry['x'], geometry['y'])
                else:
                    self.move(self.default_x, self.default_y)
            else:
                self.move(self.default_x, self.default_y)
        except Exception as e:
            print(f"Could not restore main geometry: {e}")
            self.move(self.default_x, self.default_y)
    
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
            print(f"Could not save main geometry: {e}")
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_and_raise()

    def cleanup_and_quit(self):
        print("Cleaning up and quitting...")
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            Gtk.main_quit()
        except Exception:
            pass
        self.tray_icon = None
        self.save_geometry()
        QApplication.quit()

    def closeEvent(self, event):
        if self.tray_icon:
            self.hide()
            event.ignore()
        else:
            self.cleanup_and_quit()
            event.accept()
