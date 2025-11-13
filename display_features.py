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
        self.setStyleSheet(self.get_calendar_stylesheet())
        
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
    
    def get_calendar_stylesheet(self):
        return """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #f8fffe, stop:1 #e8f5e8);
            }
            QTableWidget {
                background: white;
                border: none;
                border-radius: 15px;
                gridline-color: #e8e8e8;
                font-size: 13px;
                selection-background-color: rgba(45, 90, 39, 0.3);
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f5f5f5;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4a7c59, stop:1 #2d5a27);
                color: white;
                padding: 15px 10px;
                font-weight: 600;
                font-size: 14px;
                border: none;
                border-right: 1px solid rgba(255,255,255,0.2);
            }
            QHeaderView::section:last {
                border-right: none;
            }
            .today-cell {
                background: rgba(76, 175, 80, 0.2);
                font-weight: bold;
            }
            .weekend-cell {
                background: rgba(255, 193, 7, 0.1);
            }
        """
    
    def create_header(self):
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Previous month button
        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.clicked.connect(self.prev_month)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4a7c59, stop:1 #2d5a27);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a8c69, stop:1 #3d6a37);
            }
        """)
        layout.addWidget(self.prev_btn)
        
        # Month/Year label
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignCenter)
        self.month_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #2d5a27;
            padding: 10px;
        """)
        layout.addWidget(self.month_label, 1)
        
        # Next month button
        self.next_btn = QPushButton("Next ▶")
        self.next_btn.clicked.connect(self.next_month)
        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())
        layout.addWidget(self.next_btn)
        
        return header
    
    def create_footer(self):
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Legend
        legend = QLabel("📅 Today's date is highlighted • Weekend days have light background")
        legend.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(legend)
        
        layout.addStretch()
        
        # Export button
        export_btn = QPushButton("📄 Export PDF")
        export_btn.clicked.connect(self.export_calendar)
        export_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #f5f5f5;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #e8e8e8;
                border-color: #bbb;
            }
        """)
        layout.addWidget(export_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(self.prev_btn.styleSheet())
        layout.addWidget(close_btn)
        
        return footer
    
    def setup_calendar_table(self):
        # Set up the table structure
        self.calendar_table.setColumnCount(7)  # Date + 6 prayers
        
        # Headers
        headers = ['Date', 'Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
        translated_headers = []
        for header in headers:
            if header == 'Date':
                translated_headers.append(self.tr('prayers')['Date'])
            else:
                translated_headers.append(self.tr_prayer(header))
        
        self.calendar_table.setHorizontalHeaderLabels(translated_headers)
        
        # Table properties
        self.calendar_table.setAlternatingRowColors(True)
        self.calendar_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.calendar_table.verticalHeader().setVisible(False)
        
        # Make columns stretch
        header = self.calendar_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.resizeSection(0, 80)  # Date column
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
    
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
                
                # Date column with day name
                day_name = self.tr('days')[current_day.weekday()][:3]  # Short day name
                date_text = f"{day}\n{day_name}"
                date_item = QTableWidgetItem(date_text)
                date_item.setTextAlignment(Qt.AlignCenter)
                
                # Highlight today
                if (current_day.year == today.year and 
                    current_day.month == today.month and 
                    current_day.day == today.day):\n                    date_item.setBackground(QColor(76, 175, 80, 50))\n                    date_item.setFont(QFont(date_item.font().family(), date_item.font().pointSize(), QFont.Bold))\n                \n                # Weekend highlighting (Friday and Saturday in Morocco)\n                if current_day.weekday() in [4, 5]:  # Friday, Saturday\n                    date_item.setBackground(QColor(255, 193, 7, 25))\n                \n                self.calendar_table.setItem(row, 0, date_item)\n                \n                # Prayer times\n                if prayer_data and date_str in prayer_data:\n                    day_prayers = prayer_data[date_str]\n                    prayers = ['Fajr', 'Sunrise', 'Dohr', 'Asr', 'Maghreb', 'Isha']\n                    \n                    for col, prayer in enumerate(prayers, 1):\n                        time_text = day_prayers.get(prayer, '--:--')\n                        time_item = QTableWidgetItem(time_text)\n                        time_item.setTextAlignment(Qt.AlignCenter)\n                        \n                        # Style prayer times\n                        if time_text != '--:--':\n                            time_item.setFont(QFont(time_item.font().family(), time_item.font().pointSize(), QFont.Bold))\n                        \n                        self.calendar_table.setItem(row, col, time_item)\n                else:\n                    # No data available\n                    for col in range(1, 7):\n                        no_data_item = QTableWidgetItem('--:--')\n                        no_data_item.setTextAlignment(Qt.AlignCenter)\n                        no_data_item.setForeground(QColor(150, 150, 150))\n                        self.calendar_table.setItem(row, col, no_data_item)\n                \n                row += 1\n        \n        # Adjust row heights\n        for i in range(self.calendar_table.rowCount()):\n            self.calendar_table.setRowHeight(i, 60)\n    \n    def load_city_data(self):\n        try:\n            city_file = os.path.join(self.data_folder, f'{self.current_city.lower()}.json')\n            if os.path.exists(city_file):\n                with open(city_file, 'r', encoding='utf-8') as f:\n                    data = json.load(f)\n                    return data.get('prayer_times', {})\n        except Exception as e:\n            print(f\"Error loading city data: {e}\")\n        return {}\n    \n    def export_calendar(self):\n        # Simple export functionality\n        try:\n            from PyQt5.QtPrintSupport import QPrinter, QPrintDialog\n            from PyQt5.QtGui import QPainter, QTextDocument\n            \n            printer = QPrinter(QPrinter.HighResolution)\n            printer.setPageSize(QPrinter.A4)\n            \n            dialog = QPrintDialog(printer, self)\n            if dialog.exec_() == QPrintDialog.Accepted:\n                # Create HTML content\n                html_content = self.generate_calendar_html()\n                \n                # Print to PDF\n                document = QTextDocument()\n                document.setHtml(html_content)\n                document.print_(printer)\n                \n                QMessageBox.information(self, \"Export Complete\", \"Calendar exported successfully!\")\n        except Exception as e:\n            QMessageBox.warning(self, \"Export Error\", f\"Could not export calendar: {str(e)}\")\n    \n    def generate_calendar_html(self):\n        month_name = self.tr('months')[self.current_date.month - 1]\n        city_name = self.tr_city(self.current_city)\n        \n        html = f\"\"\"\n        <html>\n        <head>\n            <style>\n                body {{ font-family: Arial, sans-serif; margin: 20px; }}\n                h1 {{ color: #2d5a27; text-align: center; }}\n                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}\n                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}\n                th {{ background-color: #2d5a27; color: white; }}\n                .today {{ background-color: #e8f5e8; font-weight: bold; }}\n            </style>\n        </head>\n        <body>\n            <h1>Prayer Times Calendar - {city_name}</h1>\n            <h2>{month_name} {self.current_date.year}</h2>\n            <table>\n                <tr>\n                    <th>Date</th><th>Fajr</th><th>Sunrise</th><th>Dhuhr</th><th>Asr</th><th>Maghrib</th><th>Isha</th>\n                </tr>\n        \"\"\"\n        \n        # Add calendar data\n        prayer_data = self.load_city_data()\n        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)\n        today = datetime.now()\n        \n        for week in cal:\n            for day in week:\n                if day == 0:\n                    continue\n                \n                date_str = f\"{day:02d}/{self.current_date.month:02d}\"\n                current_day = datetime(self.current_date.year, self.current_date.month, day)\n                \n                is_today = (current_day.year == today.year and \n                           current_day.month == today.month and \n                           current_day.day == today.day)\n                \n                row_class = 'class=\"today\"' if is_today else ''\n                html += f\"<tr {row_class}><td>{day}</td>\"\n                \n                if prayer_data and date_str in prayer_data:\n                    day_prayers = prayer_data[date_str]\n                    for prayer in ['Fajr', 'Sunrise', 'Dohr', 'Asr', 'Maghreb', 'Isha']:\n                        time_text = day_prayers.get(prayer, '--:--')\n                        html += f\"<td>{time_text}</td>\"\n                else:\n                    html += \"<td>--:--</td>\" * 6\n                \n                html += \"</tr>\"\n        \n        html += \"\"\"\n            </table>\n        </body>\n        </html>\n        \"\"\"\n        \n        return html\n    \n    def tr(self, key):\n        return TRANSLATIONS[self.current_language].get(key, key)\n    \n    def tr_prayer(self, prayer_key):\n        return TRANSLATIONS[self.current_language]['prayers'].get(prayer_key, prayer_key)\n    \n    def tr_city(self, city_key):\n        return CITIES[city_key][self.current_language]

class WeeklyScheduleDialog(QDialog):\n    def __init__(self, current_city, current_language, parent=None):\n        super().__init__(parent)\n        self.current_city = current_city\n        self.current_language = current_language\n        self.data_folder = os.path.join(os.path.expanduser('~'), '.salah_times', 'cities')\n        self.current_date = datetime.now()\n        # Get start of week (Monday)\n        self.week_start = self.current_date - timedelta(days=self.current_date.weekday())\n        self.init_ui()\n        self.load_weekly_data()\n        \n    def init_ui(self):\n        self.setWindowTitle(f\"{self.tr('weekly_schedule')} - {self.tr_city(self.current_city)}\")\n        self.setMinimumSize(900, 600)\n        self.resize(1100, 700)\n        self.setStyleSheet(self.get_weekly_stylesheet())\n        \n        layout = QVBoxLayout(self)\n        layout.setContentsMargins(25, 25, 25, 25)\n        layout.setSpacing(20)\n        \n        # Header with navigation\n        header = self.create_header()\n        layout.addWidget(header)\n        \n        # Weekly table\n        self.weekly_table = QTableWidget()\n        self.setup_weekly_table()\n        layout.addWidget(self.weekly_table, 1)\n        \n        # Footer\n        footer = self.create_footer()\n        layout.addWidget(footer)\n    \n    def get_weekly_stylesheet(self):\n        return \"\"\"\n            QDialog {\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, \n                    stop:0 #f8fffe, stop:1 #e8f5e8);\n            }\n            QTableWidget {\n                background: white;\n                border: none;\n                border-radius: 15px;\n                gridline-color: #e8e8e8;\n                font-size: 14px;\n                selection-background-color: rgba(45, 90, 39, 0.3);\n            }\n            QTableWidget::item {\n                padding: 15px 10px;\n                border-bottom: 1px solid #f5f5f5;\n            }\n            QHeaderView::section {\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n                    stop:0 #4a7c59, stop:1 #2d5a27);\n                color: white;\n                padding: 15px 10px;\n                font-weight: 600;\n                font-size: 15px;\n                border: none;\n                border-right: 1px solid rgba(255,255,255,0.2);\n            }\n        \"\"\"\n    \n    def create_header(self):\n        header = QWidget()\n        layout = QHBoxLayout(header)\n        layout.setContentsMargins(0, 0, 0, 0)\n        \n        # Previous week button\n        self.prev_btn = QPushButton(\"◀ Previous Week\")\n        self.prev_btn.clicked.connect(self.prev_week)\n        self.prev_btn.setStyleSheet(\"\"\"\n            QPushButton {\n                padding: 12px 20px;\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n                    stop:0 #4a7c59, stop:1 #2d5a27);\n                color: white;\n                border: none;\n                border-radius: 8px;\n                font-weight: 600;\n                font-size: 14px;\n            }\n            QPushButton:hover {\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n                    stop:0 #5a8c69, stop:1 #3d6a37);\n            }\n        \"\"\")\n        layout.addWidget(self.prev_btn)\n        \n        # Week label\n        self.week_label = QLabel()\n        self.week_label.setAlignment(Qt.AlignCenter)\n        self.week_label.setStyleSheet(\"\"\"\n            font-size: 20px;\n            font-weight: 600;\n            color: #2d5a27;\n            padding: 10px;\n        \"\"\")\n        layout.addWidget(self.week_label, 1)\n        \n        # Next week button\n        self.next_btn = QPushButton(\"Next Week ▶\")\n        self.next_btn.clicked.connect(self.next_week)\n        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())\n        layout.addWidget(self.next_btn)\n        \n        return header\n    \n    def create_footer(self):\n        footer = QWidget()\n        layout = QHBoxLayout(footer)\n        layout.setContentsMargins(0, 10, 0, 0)\n        \n        # Info label\n        info = QLabel(\"📅 Weekly prayer schedule with precise timings\")\n        info.setStyleSheet(\"color: #666; font-size: 12px;\")\n        layout.addWidget(info)\n        \n        layout.addStretch()\n        \n        # Close button\n        close_btn = QPushButton(\"Close\")\n        close_btn.clicked.connect(self.close)\n        close_btn.setStyleSheet(self.prev_btn.styleSheet())\n        layout.addWidget(close_btn)\n        \n        return footer\n    \n    def setup_weekly_table(self):\n        # Set up the table structure\n        self.weekly_table.setRowCount(7)  # 7 days\n        self.weekly_table.setColumnCount(7)  # Day + 6 prayers\n        \n        # Headers\n        headers = ['Day', 'Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']\n        translated_headers = []\n        for header in headers:\n            if header == 'Day':\n                translated_headers.append('Day')\n            else:\n                translated_headers.append(self.tr_prayer(header))\n        \n        self.weekly_table.setHorizontalHeaderLabels(translated_headers)\n        \n        # Table properties\n        self.weekly_table.setAlternatingRowColors(True)\n        self.weekly_table.setSelectionBehavior(QAbstractItemView.SelectRows)\n        self.weekly_table.verticalHeader().setVisible(False)\n        \n        # Column sizing\n        header = self.weekly_table.horizontalHeader()\n        header.setSectionResizeMode(0, QHeaderView.Fixed)\n        header.resizeSection(0, 120)  # Day column\n        for i in range(1, 7):\n            header.setSectionResizeMode(i, QHeaderView.Stretch)\n        \n        # Row heights\n        for i in range(7):\n            self.weekly_table.setRowHeight(i, 70)\n    \n    def load_weekly_data(self):\n        self.update_weekly_table()\n    \n    def prev_week(self):\n        self.week_start -= timedelta(days=7)\n        self.update_weekly_table()\n    \n    def next_week(self):\n        self.week_start += timedelta(days=7)\n        self.update_weekly_table()\n    \n    def update_weekly_table(self):\n        # Update week label\n        week_end = self.week_start + timedelta(days=6)\n        start_month = self.tr('months')[self.week_start.month - 1]\n        end_month = self.tr('months')[week_end.month - 1]\n        \n        if self.week_start.month == week_end.month:\n            self.week_label.setText(f\"{self.week_start.day}-{week_end.day} {start_month} {self.week_start.year}\")\n        else:\n            self.week_label.setText(f\"{self.week_start.day} {start_month} - {week_end.day} {end_month} {self.week_start.year}\")\n        \n        # Load prayer data\n        prayer_data = self.load_city_data()\n        today = datetime.now().date()\n        \n        # Fill weekly data\n        for i in range(7):\n            current_day = self.week_start + timedelta(days=i)\n            date_str = current_day.strftime('%d/%m')\n            \n            # Day name and date\n            day_name = self.tr('days')[current_day.weekday()]\n            day_text = f\"{day_name}\\n{current_day.strftime('%d/%m/%Y')}\"\n            day_item = QTableWidgetItem(day_text)\n            day_item.setTextAlignment(Qt.AlignCenter)\n            \n            # Highlight today\n            if current_day.date() == today:\n                day_item.setBackground(QColor(76, 175, 80, 50))\n                day_item.setFont(QFont(day_item.font().family(), day_item.font().pointSize(), QFont.Bold))\n            \n            # Weekend highlighting\n            if current_day.weekday() in [4, 5]:  # Friday, Saturday\n                day_item.setBackground(QColor(255, 193, 7, 25))\n            \n            self.weekly_table.setItem(i, 0, day_item)\n            \n            # Prayer times\n            if prayer_data and date_str in prayer_data:\n                day_prayers = prayer_data[date_str]\n                prayers = ['Fajr', 'Sunrise', 'Dohr', 'Asr', 'Maghreb', 'Isha']\n                \n                for col, prayer in enumerate(prayers, 1):\n                    time_text = day_prayers.get(prayer, '--:--')\n                    time_item = QTableWidgetItem(time_text)\n                    time_item.setTextAlignment(Qt.AlignCenter)\n                    \n                    if time_text != '--:--':\n                        time_item.setFont(QFont(time_item.font().family(), 12, QFont.Bold))\n                    \n                    self.weekly_table.setItem(i, col, time_item)\n            else:\n                # No data available\n                for col in range(1, 7):\n                    no_data_item = QTableWidgetItem('--:--')\n                    no_data_item.setTextAlignment(Qt.AlignCenter)\n                    no_data_item.setForeground(QColor(150, 150, 150))\n                    self.weekly_table.setItem(i, col, no_data_item)\n    \n    def load_city_data(self):\n        try:\n            city_file = os.path.join(self.data_folder, f'{self.current_city.lower()}.json')\n            if os.path.exists(city_file):\n                with open(city_file, 'r', encoding='utf-8') as f:\n                    data = json.load(f)\n                    return data.get('prayer_times', {})\n        except Exception as e:\n            print(f\"Error loading city data: {e}\")\n        return {}\n    \n    def tr(self, key):\n        return TRANSLATIONS[self.current_language].get(key, key)\n    \n    def tr_prayer(self, prayer_key):\n        return TRANSLATIONS[self.current_language]['prayers'].get(prayer_key, prayer_key)\n    \n    def tr_city(self, city_key):\n        return CITIES[city_key][self.current_language]

class TimezoneViewDialog(QDialog):\n    def __init__(self, current_city, current_language, parent=None):\n        super().__init__(parent)\n        self.current_city = current_city\n        self.current_language = current_language\n        self.data_folder = os.path.join(os.path.expanduser('~'), '.salah_times', 'cities')\n        # Default major cities for comparison\n        self.selected_cities = ['Tangier', 'Casablanca', 'Rabat', 'Marrakech', 'Fes', 'Agadir']\n        if self.current_city not in self.selected_cities:\n            self.selected_cities.insert(0, self.current_city)\n        self.init_ui()\n        self.load_timezone_data()\n        \n    def init_ui(self):\n        self.setWindowTitle(self.tr('timezone_view'))\n        self.setMinimumSize(1100, 700)\n        self.resize(1300, 800)\n        self.setStyleSheet(self.get_timezone_stylesheet())\n        \n        layout = QVBoxLayout(self)\n        layout.setContentsMargins(25, 25, 25, 25)\n        layout.setSpacing(20)\n        \n        # Header with controls\n        header = self.create_header()\n        layout.addWidget(header)\n        \n        # Timezone comparison table\n        self.timezone_table = QTableWidget()\n        self.setup_timezone_table()\n        layout.addWidget(self.timezone_table, 1)\n        \n        # Footer with info\n        footer = self.create_footer()\n        layout.addWidget(footer)\n    \n    def get_timezone_stylesheet(self):\n        return \"\"\"\n            QDialog {\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, \n                    stop:0 #f8fffe, stop:1 #e8f5e8);\n            }\n            QTableWidget {\n                background: white;\n                border: none;\n                border-radius: 15px;\n                gridline-color: #e8e8e8;\n                font-size: 13px;\n                selection-background-color: rgba(45, 90, 39, 0.3);\n            }\n            QTableWidget::item {\n                padding: 12px 8px;\n                border-bottom: 1px solid #f5f5f5;\n            }\n            QHeaderView::section {\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n                    stop:0 #4a7c59, stop:1 #2d5a27);\n                color: white;\n                padding: 15px 10px;\n                font-weight: 600;\n                font-size: 14px;\n                border: none;\n                border-right: 1px solid rgba(255,255,255,0.2);\n            }\n        \"\"\"\n    \n    def create_header(self):\n        header = QWidget()\n        layout = QHBoxLayout(header)\n        layout.setContentsMargins(0, 0, 0, 0)\n        \n        # Title\n        title = QLabel(\"🌍 Multi-City Prayer Times Comparison\")\n        title.setStyleSheet(\"\"\"\n            font-size: 22px;\n            font-weight: 600;\n            color: #2d5a27;\n            padding: 10px 0;\n        \"\"\")\n        layout.addWidget(title)\n        \n        layout.addStretch()\n        \n        # Refresh button\n        refresh_btn = QPushButton(\"🔄 Refresh All\")\n        refresh_btn.clicked.connect(self.load_timezone_data)\n        refresh_btn.setStyleSheet(\"\"\"\n            QPushButton {\n                padding: 10px 20px;\n                background: #f5f5f5;\n                color: #333;\n                border: 2px solid #ddd;\n                border-radius: 8px;\n                font-weight: 600;\n            }\n            QPushButton:hover {\n                background: #e8e8e8;\n                border-color: #bbb;\n            }\n        \"\"\")\n        layout.addWidget(refresh_btn)\n        \n        # Add city button\n        add_city_btn = QPushButton(\"+ Add City\")\n        add_city_btn.clicked.connect(self.add_city)\n        add_city_btn.setStyleSheet(\"\"\"\n            QPushButton {\n                padding: 10px 20px;\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n                    stop:0 #4a7c59, stop:1 #2d5a27);\n                color: white;\n                border: none;\n                border-radius: 8px;\n                font-weight: 600;\n            }\n            QPushButton:hover {\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n                    stop:0 #5a8c69, stop:1 #3d6a37);\n            }\n        \"\"\")\n        layout.addWidget(add_city_btn)\n        \n        return header\n    \n    def create_footer(self):\n        footer = QWidget()\n        layout = QHBoxLayout(footer)\n        layout.setContentsMargins(0, 10, 0, 0)\n        \n        # Info about timezones\n        info = QLabel(\"ℹ️ All Moroccan cities use the same timezone (UTC+1). Differences in prayer times are due to geographical location.\")\n        info.setStyleSheet(\"color: #666; font-size: 12px;\")\n        info.setWordWrap(True)\n        layout.addWidget(info)\n        \n        layout.addStretch()\n        \n        # Close button\n        close_btn = QPushButton(\"Close\")\n        close_btn.clicked.connect(self.close)\n        close_btn.setStyleSheet(\"\"\"\n            QPushButton {\n                padding: 12px 24px;\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n                    stop:0 #4a7c59, stop:1 #2d5a27);\n                color: white;\n                border: none;\n                border-radius: 8px;\n                font-weight: 600;\n            }\n            QPushButton:hover {\n                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n                    stop:0 #5a8c69, stop:1 #3d6a37);\n            }\n        \"\"\")\n        layout.addWidget(close_btn)\n        \n        return footer\n    \n    def setup_timezone_table(self):\n        # Set up the table structure\n        self.timezone_table.setRowCount(len(self.selected_cities))\n        self.timezone_table.setColumnCount(9)  # City + Coordinates + Local Time + 6 prayers\n        \n        # Headers\n        headers = ['City', 'Coordinates', 'Local Time', 'Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']\n        translated_headers = []\n        for header in headers:\n            if header in ['City', 'Coordinates', 'Local Time']:\n                translated_headers.append(header)\n            else:\n                translated_headers.append(self.tr_prayer(header))\n        \n        self.timezone_table.setHorizontalHeaderLabels(translated_headers)\n        \n        # Table properties\n        self.timezone_table.setAlternatingRowColors(True)\n        self.timezone_table.setSelectionBehavior(QAbstractItemView.SelectRows)\n        self.timezone_table.verticalHeader().setVisible(False)\n        \n        # Column sizing\n        header = self.timezone_table.horizontalHeader()\n        header.setSectionResizeMode(0, QHeaderView.Fixed)\n        header.resizeSection(0, 120)  # City column\n        header.setSectionResizeMode(1, QHeaderView.Fixed)\n        header.resizeSection(1, 140)  # Coordinates column\n        header.setSectionResizeMode(2, QHeaderView.Fixed)\n        header.resizeSection(2, 100)  # Local time column\n        for i in range(3, 9):\n            header.setSectionResizeMode(i, QHeaderView.Stretch)\n        \n        # Row heights\n        for i in range(len(self.selected_cities)):\n            self.timezone_table.setRowHeight(i, 50)\n    \n    def add_city(self):\n        # Get available cities not already selected\n        available_cities = [city for city in CITIES.keys() if city not in self.selected_cities]\n        if not available_cities:\n            QMessageBox.information(self, \"No More Cities\", \"All available cities are already displayed.\")\n            return\n        \n        # Show selection dialog\n        dialog = QDialog(self)\n        dialog.setWindowTitle(\"Add City\")\n        dialog.setModal(True)\n        dialog.resize(300, 400)\n        \n        layout = QVBoxLayout(dialog)\n        \n        label = QLabel(\"Select a city to add:\")\n        layout.addWidget(label)\n        \n        city_list = QListWidget()\n        for city in sorted(available_cities):\n            city_list.addItem(self.tr_city(city))\n        layout.addWidget(city_list)\n        \n        buttons = QHBoxLayout()\n        cancel_btn = QPushButton(\"Cancel\")\n        cancel_btn.clicked.connect(dialog.reject)\n        add_btn = QPushButton(\"Add\")\n        add_btn.clicked.connect(dialog.accept)\n        buttons.addWidget(cancel_btn)\n        buttons.addWidget(add_btn)\n        layout.addLayout(buttons)\n        \n        if dialog.exec_() == QDialog.Accepted and city_list.currentItem():\n            selected_city_name = city_list.currentItem().text()\n            # Find the city key\n            for city_key in available_cities:\n                if self.tr_city(city_key) == selected_city_name:\n                    self.selected_cities.append(city_key)\n                    self.setup_timezone_table()\n                    self.load_timezone_data()\n                    break\n    \n    def load_timezone_data(self):\n        today = datetime.now().strftime('%d/%m')\n        current_time = datetime.now()\n        \n        # Update table size\n        self.timezone_table.setRowCount(len(self.selected_cities))\n        \n        # Fill data for each city\n        for row, city in enumerate(self.selected_cities):\n            # City name\n            city_name = self.tr_city(city)\n            city_item = QTableWidgetItem(city_name)\n            city_item.setTextAlignment(Qt.AlignCenter)\n            \n            # Highlight current city\n            if city == self.current_city:\n                city_item.setBackground(QColor(76, 175, 80, 100))\n                city_item.setFont(QFont(city_item.font().family(), city_item.font().pointSize(), QFont.Bold))\n            \n            self.timezone_table.setItem(row, 0, city_item)\n            \n            # Coordinates\n            if city in CITIES and 'lat' in CITIES[city] and 'lon' in CITIES[city]:\n                lat = CITIES[city]['lat']\n                lon = CITIES[city]['lon']\n                coord_text = f\"{lat:.2f}°, {lon:.2f}°\"\n            else:\n                coord_text = \"N/A\"\n            \n            coord_item = QTableWidgetItem(coord_text)\n            coord_item.setTextAlignment(Qt.AlignCenter)\n            self.timezone_table.setItem(row, 1, coord_item)\n            \n            # Local time (same for all Morocco cities - UTC+1)\n            time_item = QTableWidgetItem(current_time.strftime('%H:%M'))\n            time_item.setTextAlignment(Qt.AlignCenter)\n            self.timezone_table.setItem(row, 2, time_item)\n            \n            # Load prayer data for this city\n            prayer_data = self.load_city_data(city)\n            \n            if prayer_data and today in prayer_data:\n                day_prayers = prayer_data[today]\n                prayers = ['Fajr', 'Sunrise', 'Dohr', 'Asr', 'Maghreb', 'Isha']\n                \n                for col, prayer in enumerate(prayers, 3):\n                    time_text = day_prayers.get(prayer, '--:--')\n                    time_item = QTableWidgetItem(time_text)\n                    time_item.setTextAlignment(Qt.AlignCenter)\n                    \n                    # Highlight current city\n                    if city == self.current_city:\n                        time_item.setBackground(QColor(76, 175, 80, 50))\n                    \n                    if time_text != '--:--':\n                        time_item.setFont(QFont(time_item.font().family(), time_item.font().pointSize(), QFont.Bold))\n                    \n                    self.timezone_table.setItem(row, col, time_item)\n            else:\n                # No data available\n                for col in range(3, 9):\n                    no_data_item = QTableWidgetItem('--:--')\n                    no_data_item.setTextAlignment(Qt.AlignCenter)\n                    no_data_item.setForeground(QColor(150, 150, 150))\n                    self.timezone_table.setItem(row, col, no_data_item)\n    \n    def load_city_data(self, city):\n        try:\n            city_file = os.path.join(self.data_folder, f'{city.lower()}.json')\n            if os.path.exists(city_file):\n                with open(city_file, 'r', encoding='utf-8') as f:\n                    data = json.load(f)\n                    return data.get('prayer_times', {})\n        except Exception as e:\n            print(f\"Error loading city data for {city}: {e}\")\n        return {}\n    \n    def tr(self, key):\n        return TRANSLATIONS[self.current_language].get(key, key)\n    \n    def tr_prayer(self, prayer_key):\n        return TRANSLATIONS[self.current_language]['prayers'].get(prayer_key, prayer_key)\n    \n    def tr_city(self, city_key):\n        return CITIES[city_key][self.current_language]