import calendar
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .constants import TRANSLATIONS, CITIES
from .database import get_all_prayer_times


class MonthlyCalendarDialog(QDialog):
    def __init__(self, current_city, current_language, parent=None):
        super().__init__(parent)
        self.current_city = current_city
        self.current_language = current_language
        self.current_date = datetime.now()
        self.init_ui()
        self.update_calendar()

    def init_ui(self):
        self.setWindowTitle(f"{self.tr('monthly_calendar')} - {self.tr_city(self.current_city)}")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        layout.addWidget(self._header())
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Date', 'Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha'])
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table, 1)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def _header(self):
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        prev = QPushButton("◀ Previous")
        prev.clicked.connect(self.prev_month)
        layout.addWidget(prev)
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.month_label, 1)
        nxt = QPushButton("Next ▶")
        nxt.clicked.connect(self.next_month)
        layout.addWidget(nxt)
        return w

    def prev_month(self):
        m, y = self.current_date.month, self.current_date.year
        self.current_date = self.current_date.replace(month=12 if m == 1 else m - 1,
                                                       year=y - 1 if m == 1 else y)
        self.update_calendar()

    def next_month(self):
        m, y = self.current_date.month, self.current_date.year
        self.current_date = self.current_date.replace(month=1 if m == 12 else m + 1,
                                                       year=y + 1 if m == 12 else y)
        self.update_calendar()

    def update_calendar(self):
        self.month_label.setText(f"{self.tr('months')[self.current_date.month - 1]} {self.current_date.year}")
        prayer_data = get_all_prayer_times(self.current_city)
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        days = [d for week in cal for d in week if d != 0]
        self.table.setRowCount(len(days))
        today = datetime.now()
        for row, day in enumerate(days):
            date_str = f"{day:02d}/{self.current_date.month:02d}"
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            if (self.current_date.year == today.year and
                    self.current_date.month == today.month and day == today.day):
                date_item.setBackground(QColor(76, 175, 80, 80))
            self.table.setItem(row, 0, date_item)
            day_prayers = prayer_data.get(date_str, {})
            for col, prayer in enumerate(['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha'], 1):
                item = QTableWidgetItem(day_prayers.get(prayer, '--:--'))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)

    def tr_city(self, city_key):
        return CITIES[city_key][self.current_language]


class WeeklyScheduleDialog(QDialog):
    def __init__(self, current_city, current_language, parent=None):
        super().__init__(parent)
        self.current_city = current_city
        self.current_language = current_language
        self.week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        self.init_ui()
        self.update_table()

    def init_ui(self):
        self.setWindowTitle(f"{self.tr('weekly_schedule')} - {self.tr_city(self.current_city)}")
        self.setMinimumSize(900, 500)
        self.resize(1100, 650)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        layout.addWidget(self._header())
        self.table = QTableWidget(7, 6)
        self.table.setHorizontalHeaderLabels(['Day', 'Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha'])
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table, 1)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def _header(self):
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        prev = QPushButton("◀ Previous Week")
        prev.clicked.connect(lambda: self._shift(-7))
        layout.addWidget(prev)
        self.week_label = QLabel()
        self.week_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.week_label, 1)
        nxt = QPushButton("Next Week ▶")
        nxt.clicked.connect(lambda: self._shift(7))
        layout.addWidget(nxt)
        return w

    def _shift(self, days):
        self.week_start += timedelta(days=days)
        self.update_table()

    def update_table(self):
        week_end = self.week_start + timedelta(days=6)
        sm = self.tr('months')[self.week_start.month - 1]
        em = self.tr('months')[week_end.month - 1]
        if self.week_start.month == week_end.month:
            self.week_label.setText(f"{self.week_start.day}-{week_end.day} {sm} {self.week_start.year}")
        else:
            self.week_label.setText(f"{self.week_start.day} {sm} - {week_end.day} {em} {self.week_start.year}")
        prayer_data = get_all_prayer_times(self.current_city)
        today = datetime.now().date()
        for i in range(7):
            day = self.week_start + timedelta(days=i)
            date_str = day.strftime('%d/%m')
            day_item = QTableWidgetItem(f"{self.tr('days')[day.weekday()]}\n{date_str}")
            day_item.setTextAlignment(Qt.AlignCenter)
            if day.date() == today:
                day_item.setBackground(QColor(76, 175, 80, 80))
            self.table.setItem(i, 0, day_item)
            day_prayers = prayer_data.get(date_str, {})
            for col, prayer in enumerate(['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha'], 1):
                item = QTableWidgetItem(day_prayers.get(prayer, '--:--'))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, col, item)

    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)

    def tr_city(self, city_key):
        return CITIES[city_key][self.current_language]


class TimezoneViewDialog(QDialog):
    def __init__(self, current_city, current_language, parent=None):
        super().__init__(parent)
        self.current_city = current_city
        self.current_language = current_language
        self.selected_cities = ['Tangier', 'Casablanca', 'Rabat', 'Marrakech', 'Fes', 'Agadir']
        if self.current_city not in self.selected_cities:
            self.selected_cities.insert(0, self.current_city)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle(self.tr('timezone_view'))
        self.setMinimumSize(1100, 600)
        self.resize(1300, 750)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        header = QWidget()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.addWidget(QLabel("🌍 Multi-City Prayer Times Comparison"))
        hl.addStretch()
        add_btn = QPushButton("+ Add City")
        add_btn.clicked.connect(self.add_city)
        hl.addWidget(add_btn)
        layout.addWidget(header)
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ['City', 'Local Time', 'Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha', ''])
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table, 1)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def add_city(self):
        available = [c for c in CITIES if c not in self.selected_cities]
        if not available:
            QMessageBox.information(self, "No More Cities", "All cities are already displayed.")
            return
        city, ok = QInputDialog.getItem(self, "Add City", "Select city:", available, 0, False)
        if ok and city:
            self.selected_cities.append(city)
            self.load_data()

    def load_data(self):
        today = datetime.now().strftime('%d/%m')
        now_str = datetime.now().strftime('%H:%M')
        self.table.setRowCount(len(self.selected_cities))
        for row, city in enumerate(self.selected_cities):
            city_item = QTableWidgetItem(CITIES[city][self.current_language])
            city_item.setTextAlignment(Qt.AlignCenter)
            if city == self.current_city:
                city_item.setBackground(QColor(76, 175, 80, 100))
            self.table.setItem(row, 0, city_item)
            time_item = QTableWidgetItem(now_str)
            time_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, time_item)
            prayer_data = get_all_prayer_times(city)
            day_prayers = prayer_data.get(today, {})
            for col, prayer in enumerate(['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha'], 2):
                item = QTableWidgetItem(day_prayers.get(prayer, '--:--'))
                item.setTextAlignment(Qt.AlignCenter)
                if city == self.current_city:
                    item.setBackground(QColor(76, 175, 80, 50))
                self.table.setItem(row, col, item)

    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)

    def tr_city(self, city_key):
        return CITIES[city_key][self.current_language]
