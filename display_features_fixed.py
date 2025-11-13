#!/usr/bin/env python3
import sys
import os
import json
import calendar
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Import from main app
from ultra_modern_salah import TRANSLATIONS, CITIES

class MonthlyCalendarDialog(QDialog):
    def __init__(self, current_city, current_language, parent=None):
        super().__init__(parent)
        self.current_city = current_city
        self.current_language = current_language
        self.data_folder = os.path.join(os.path.expanduser('~'), '.salah_times', 'cities')
        self.current_date = datetime.now()
        self.init_ui()
        self.load_monthly_data()
        
    def init_ui(self):
        self.setWindowTitle(f"{self.tr('monthly_calendar')} - {self.tr_city(self.current_city)}")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header with navigation
        header = self.create_header()
        layout.addWidget(header)
        
        # Calendar table
        self.calendar_table = QTableWidget()
        self.setup_calendar_table()
        layout.addWidget(self.calendar_table, 1)
        
        # Footer with buttons
        footer = self.create_footer()
        layout.addWidget(footer)
    
    def create_header(self):
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Previous month button
        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.clicked.connect(self.prev_month)
        layout.addWidget(self.prev_btn)
        
        # Month/Year label
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.month_label, 1)
        
        # Next month button
        self.next_btn = QPushButton("Next ▶")
        self.next_btn.clicked.connect(self.next_month)
        layout.addWidget(self.next_btn)
        
        return header
    
    def create_footer(self):
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return footer
    
    def setup_calendar_table(self):
        # Set up the table structure
        self.calendar_table.setColumnCount(7)  # Date + 6 prayers
        
        # Headers
        headers = ['Date', 'Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
        self.calendar_table.setHorizontalHeaderLabels(headers)
        
        # Table properties
        self.calendar_table.setAlternatingRowColors(True)
        self.calendar_table.verticalHeader().setVisible(False)
    
    def load_monthly_data(self):
        self.update_calendar()
    
    def prev_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
    
    def update_calendar(self):
        # Update month label
        month_name = self.tr('months')[self.current_date.month - 1]
        self.month_label.setText(f"{month_name} {self.current_date.year}")
        
        # Load prayer data for this month
        prayer_data = self.load_city_data()
        
        # Get calendar for this month
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Calculate total rows needed
        total_days = sum(1 for week in cal for day in week if day != 0)
        self.calendar_table.setRowCount(total_days)
        
        # Fill calendar data
        row = 0
        today = datetime.now()
        
        for week in cal:
            for day in week:
                if day == 0:
                    continue
                
                date_str = f"{day:02d}/{self.current_date.month:02d}"
                current_day = datetime(self.current_date.year, self.current_date.month, day)
                
                # Date column
                date_item = QTableWidgetItem(str(day))
                date_item.setTextAlignment(Qt.AlignCenter)
                
                # Highlight today
                if (current_day.year == today.year and 
                    current_day.month == today.month and 
                    current_day.day == today.day):
                    date_item.setBackground(QColor(76, 175, 80, 50))
                
                self.calendar_table.setItem(row, 0, date_item)
                
                # Prayer times
                if prayer_data and date_str in prayer_data:
                    day_prayers = prayer_data[date_str]
                    prayers = ['Fajr', 'Sunrise', 'Dohr', 'Asr', 'Maghreb', 'Isha']
                    
                    for col, prayer in enumerate(prayers, 1):
                        time_text = day_prayers.get(prayer, '--:--')
                        time_item = QTableWidgetItem(time_text)
                        time_item.setTextAlignment(Qt.AlignCenter)
                        self.calendar_table.setItem(row, col, time_item)
                else:
                    # No data available
                    for col in range(1, 7):
                        no_data_item = QTableWidgetItem('--:--')
                        no_data_item.setTextAlignment(Qt.AlignCenter)
                        self.calendar_table.setItem(row, col, no_data_item)
                
                row += 1
    
    def load_city_data(self):
        try:
            city_file = os.path.join(self.data_folder, f'{self.current_city.lower()}.json')
            if os.path.exists(city_file):
                with open(city_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('prayer_times', {})
        except Exception as e:
            print(f"Error loading city data: {e}")
        return {}
    
    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)
    
    def tr_prayer(self, prayer_key):
        return TRANSLATIONS[self.current_language]['prayers'].get(prayer_key, prayer_key)
    
    def tr_city(self, city_key):
        return CITIES[city_key][self.current_language]

class WeeklyScheduleDialog(QDialog):
    def __init__(self, current_city, current_language, parent=None):
        super().__init__(parent)
        self.current_city = current_city
        self.current_language = current_language
        self.data_folder = os.path.join(os.path.expanduser('~'), '.salah_times', 'cities')
        self.current_date = datetime.now()
        # Get start of week (Monday)
        self.week_start = self.current_date - timedelta(days=self.current_date.weekday())
        self.init_ui()
        self.load_weekly_data()
        
    def init_ui(self):
        self.setWindowTitle(f"{self.tr('weekly_schedule')} - {self.tr_city(self.current_city)}")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header with navigation
        header = self.create_header()
        layout.addWidget(header)
        
        # Weekly table
        self.weekly_table = QTableWidget()
        self.setup_weekly_table()
        layout.addWidget(self.weekly_table, 1)
        
        # Footer
        footer = self.create_footer()
        layout.addWidget(footer)
    
    def create_header(self):
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Previous week button
        self.prev_btn = QPushButton("◀ Previous Week")
        self.prev_btn.clicked.connect(self.prev_week)
        layout.addWidget(self.prev_btn)
        
        # Week label
        self.week_label = QLabel()
        self.week_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.week_label, 1)
        
        # Next week button
        self.next_btn = QPushButton("Next Week ▶")
        self.next_btn.clicked.connect(self.next_week)
        layout.addWidget(self.next_btn)
        
        return header
    
    def create_footer(self):
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return footer
    
    def setup_weekly_table(self):
        # Set up the table structure
        self.weekly_table.setRowCount(7)  # 7 days
        self.weekly_table.setColumnCount(7)  # Day + 6 prayers
        
        # Headers
        headers = ['Day', 'Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
        self.weekly_table.setHorizontalHeaderLabels(headers)
        
        # Table properties
        self.weekly_table.setAlternatingRowColors(True)
        self.weekly_table.verticalHeader().setVisible(False)
    
    def load_weekly_data(self):
        self.update_weekly_table()
    
    def prev_week(self):
        self.week_start -= timedelta(days=7)
        self.update_weekly_table()
    
    def next_week(self):
        self.week_start += timedelta(days=7)
        self.update_weekly_table()
    
    def update_weekly_table(self):
        # Update week label
        week_end = self.week_start + timedelta(days=6)
        start_month = self.tr('months')[self.week_start.month - 1]
        end_month = self.tr('months')[week_end.month - 1]
        
        if self.week_start.month == week_end.month:
            self.week_label.setText(f"{self.week_start.day}-{week_end.day} {start_month} {self.week_start.year}")
        else:
            self.week_label.setText(f"{self.week_start.day} {start_month} - {week_end.day} {end_month} {self.week_start.year}")
        
        # Load prayer data
        prayer_data = self.load_city_data()
        today = datetime.now().date()
        
        # Fill weekly data
        for i in range(7):
            current_day = self.week_start + timedelta(days=i)
            date_str = current_day.strftime('%d/%m')
            
            # Day name and date
            day_name = self.tr('days')[current_day.weekday()]
            day_text = f"{day_name}\n{current_day.strftime('%d/%m/%Y')}"
            day_item = QTableWidgetItem(day_text)
            day_item.setTextAlignment(Qt.AlignCenter)
            
            # Highlight today
            if current_day.date() == today:
                day_item.setBackground(QColor(76, 175, 80, 50))
            
            self.weekly_table.setItem(i, 0, day_item)
            
            # Prayer times
            if prayer_data and date_str in prayer_data:
                day_prayers = prayer_data[date_str]
                prayers = ['Fajr', 'Sunrise', 'Dohr', 'Asr', 'Maghreb', 'Isha']
                
                for col, prayer in enumerate(prayers, 1):
                    time_text = day_prayers.get(prayer, '--:--')
                    time_item = QTableWidgetItem(time_text)
                    time_item.setTextAlignment(Qt.AlignCenter)
                    self.weekly_table.setItem(i, col, time_item)
            else:
                # No data available
                for col in range(1, 7):
                    no_data_item = QTableWidgetItem('--:--')
                    no_data_item.setTextAlignment(Qt.AlignCenter)
                    self.weekly_table.setItem(i, col, no_data_item)
    
    def load_city_data(self):
        try:
            city_file = os.path.join(self.data_folder, f'{self.current_city.lower()}.json')
            if os.path.exists(city_file):
                with open(city_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('prayer_times', {})
        except Exception as e:
            print(f"Error loading city data: {e}")
        return {}
    
    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)
    
    def tr_prayer(self, prayer_key):
        return TRANSLATIONS[self.current_language]['prayers'].get(prayer_key, prayer_key)
    
    def tr_city(self, city_key):
        return CITIES[city_key][self.current_language]

class TimezoneViewDialog(QDialog):
    def __init__(self, current_city, current_language, parent=None):
        super().__init__(parent)
        self.current_city = current_city
        self.current_language = current_language
        self.data_folder = os.path.join(os.path.expanduser('~'), '.salah_times', 'cities')
        # Default major cities for comparison
        self.selected_cities = ['Tangier', 'Casablanca', 'Rabat', 'Marrakech', 'Fes', 'Agadir']
        if self.current_city not in self.selected_cities:
            self.selected_cities.insert(0, self.current_city)
        self.init_ui()
        self.load_timezone_data()
        
    def init_ui(self):
        self.setWindowTitle(self.tr('timezone_view'))
        self.setMinimumSize(1100, 700)
        self.resize(1300, 800)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header with controls
        header = self.create_header()
        layout.addWidget(header)
        
        # Timezone comparison table
        self.timezone_table = QTableWidget()
        self.setup_timezone_table()
        layout.addWidget(self.timezone_table, 1)
        
        # Footer with info
        footer = self.create_footer()
        layout.addWidget(footer)
    
    def create_header(self):
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("🌍 Multi-City Prayer Times Comparison")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Add city button
        add_city_btn = QPushButton("+ Add City")
        add_city_btn.clicked.connect(self.add_city)
        layout.addWidget(add_city_btn)
        
        return header
    
    def create_footer(self):
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return footer
    
    def setup_timezone_table(self):
        # Set up the table structure
        self.timezone_table.setRowCount(len(self.selected_cities))
        self.timezone_table.setColumnCount(8)  # City + Local Time + 6 prayers
        
        # Headers
        headers = ['City', 'Local Time', 'Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
        self.timezone_table.setHorizontalHeaderLabels(headers)
        
        # Table properties
        self.timezone_table.setAlternatingRowColors(True)
        self.timezone_table.verticalHeader().setVisible(False)
    
    def add_city(self):
        # Get available cities not already selected
        available_cities = [city for city in CITIES.keys() if city not in self.selected_cities]
        if not available_cities:
            QMessageBox.information(self, "No More Cities", "All available cities are already displayed.")
            return
        
        # Simple selection
        city, ok = QInputDialog.getItem(self, "Add City", "Select city to add:", available_cities, 0, False)
        if ok and city:
            self.selected_cities.append(city)
            self.setup_timezone_table()
            self.load_timezone_data()
    
    def load_timezone_data(self):
        today = datetime.now().strftime('%d/%m')
        current_time = datetime.now()
        
        # Update table size
        self.timezone_table.setRowCount(len(self.selected_cities))
        
        # Fill data for each city
        for row, city in enumerate(self.selected_cities):
            # City name
            city_name = self.tr_city(city)
            city_item = QTableWidgetItem(city_name)
            city_item.setTextAlignment(Qt.AlignCenter)
            
            # Highlight current city
            if city == self.current_city:
                city_item.setBackground(QColor(76, 175, 80, 100))
            
            self.timezone_table.setItem(row, 0, city_item)
            
            # Local time (same for all Morocco cities - UTC+1)
            time_item = QTableWidgetItem(current_time.strftime('%H:%M'))
            time_item.setTextAlignment(Qt.AlignCenter)
            self.timezone_table.setItem(row, 1, time_item)
            
            # Load prayer data for this city
            prayer_data = self.load_city_data(city)
            
            if prayer_data and today in prayer_data:
                day_prayers = prayer_data[today]
                prayers = ['Fajr', 'Sunrise', 'Dohr', 'Asr', 'Maghreb', 'Isha']
                
                for col, prayer in enumerate(prayers, 2):
                    time_text = day_prayers.get(prayer, '--:--')
                    time_item = QTableWidgetItem(time_text)
                    time_item.setTextAlignment(Qt.AlignCenter)
                    
                    # Highlight current city
                    if city == self.current_city:
                        time_item.setBackground(QColor(76, 175, 80, 50))
                    
                    self.timezone_table.setItem(row, col, time_item)
            else:
                # No data available
                for col in range(2, 8):
                    no_data_item = QTableWidgetItem('--:--')
                    no_data_item.setTextAlignment(Qt.AlignCenter)
                    self.timezone_table.setItem(row, col, no_data_item)
    
    def load_city_data(self, city):
        try:
            city_file = os.path.join(self.data_folder, f'{city.lower()}.json')
            if os.path.exists(city_file):
                with open(city_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('prayer_times', {})
        except Exception as e:
            print(f"Error loading city data for {city}: {e}")
        return {}
    
    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)
    
    def tr_prayer(self, prayer_key):
        return TRANSLATIONS[self.current_language]['prayers'].get(prayer_key, prayer_key)
    
    def tr_city(self, city_key):
        return CITIES[city_key][self.current_language]