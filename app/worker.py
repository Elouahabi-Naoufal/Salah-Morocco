import os
import json
from PyQt5.QtCore import QThread, pyqtSignal
from .database import (
    get_today_prayer_times, update_all_cities, check_internet,
    db_exists, reset_day_counter, get_day_counter
)


class PrayerTimeWorker(QThread):
    data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    offline_data_loaded = pyqtSignal(dict, int)
    db_refresh_needed = pyqtSignal()

    def __init__(self, city_name='Tangier'):
        super().__init__()
        self.city_name = city_name

    def run(self):
        self.load_cached_data_immediately()
        if not db_exists():
            self.update_data_in_background()
        elif get_day_counter() >= 30:
            self.db_refresh_needed.emit()

    def load_cached_data_immediately(self):
        row = get_today_prayer_times(self.city_name)
        if row:
            self.data_received.emit(row)
        else:
            self.force_update_data()

    def update_data_in_background(self):
        if check_internet():
            try:
                update_all_cities()
                reset_day_counter()
            except Exception as e:
                print(f"Background update failed: {e}")

    def force_update_data(self):
        if check_internet():
            try:
                update_all_cities()
                reset_day_counter()
                row = get_today_prayer_times(self.city_name)
                if row:
                    self.data_received.emit(row)
                else:
                    self.error_occurred.emit("No prayer times found for today")
            except Exception as e:
                self.error_occurred.emit(f"Update failed: {str(e)}")
        else:
            self.error_occurred.emit("No internet connection and no offline data available")
