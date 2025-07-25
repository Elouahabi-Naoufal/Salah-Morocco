#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import threading
import json
import os

# Translation dictionaries
TRANSLATIONS = {
    'en': {
        'app_title': 'Salah Times',
        'next_prayer': 'NEXT PRAYER',
        'tomorrow': 'Tomorrow',
        'loading': '🔄 Loading prayer times...',
        'refresh': '↻ Refresh',
        'error': '⚠️ Error: {}\n\nPlease check your internet connection\nand try refreshing.',
        'welcome': '🕌 Welcome to Salah Times',
        'select_city': 'Please select your default city for prayer times:',
        'search_city': 'Search for a city...',
        'cancel': 'Cancel',
        'set_default': 'Set as Default',
        'change_city': 'Change Default City',
        'iqama_time': 'Time before Iqama of {}: {:02d}:{:02d}:{:02d}',
        'iqama_passed': 'Iqama of {}: 00:00:00',
        'hijri_unavailable': 'Hijri date unavailable',
        'hijri_approx': '{} AH (Approximate)',
        'morocco': 'Morocco',
        'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'hijri_months': {'Muharram': 'Muharram', 'Safar': 'Safar', 'Rabi\'al-awwal': 'Rabi al-Awwal', 'Rabi\'al-thani': 'Rabi al-Thani', 'Jumada al-awwal': 'Jumada al-Awwal', 'Jumada al-thani': 'Jumada al-Thani', 'Rajab': 'Rajab', 'Sha\'ban': 'Shaban', 'Ramadan': 'Ramadan', 'Shawwal': 'Shawwal', 'Dhu al-Qi\'dah': 'Dhu al-Qidah', 'Dhu al-Hijjah': 'Dhu al-Hijjah'},
        'language': 'Language',
        'settings': 'Settings',
        'prayers': {
            'Date': 'Date',
            'Fajr': 'Fajr',
            'Sunrise': 'Sunrise', 
            'Dohr': 'Dhuhr',
            'Asr': 'Asr',
            'Maghreb': 'Maghrib',
            'Isha': 'Isha'
        }
    },
    'ar': {
        'app_title': 'مواقيت الصلاة',
        'next_prayer': 'الصلاة القادمة',
        'tomorrow': 'غداً',
        'loading': '🔄 جاري تحميل مواقيت الصلاة...',
        'refresh': '↻ تحديث',
        'error': '⚠️ خطأ: {}\n\nيرجى التحقق من اتصال الإنترنت\nوإعادة المحاولة.',
        'welcome': '🕌 مرحباً بك في مواقيت الصلاة',
        'select_city': 'يرجى اختيار مدينتك الافتراضية لمواقيت الصلاة:',
        'search_city': 'البحث عن مدينة...',
        'cancel': 'إلغاء',
        'set_default': 'تعيين كافتراضي',
        'change_city': 'تغيير المدينة الافتراضية',
        'iqama_time': 'الوقت المتبقي لإقامة {}: {:02d}:{:02d}:{:02d}',
        'iqama_passed': 'إقامة {}: 00:00:00',
        'hijri_unavailable': 'التاريخ الهجري غير متوفر',
        'hijri_approx': '{} هـ (تقريبي)',
        'morocco': 'المغرب',
        'months': ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'],
        'days': ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد'],
        'hijri_months': {'Muharram': 'محرم', 'Safar': 'صفر', 'Rabi\'al-awwal': 'ربيع الأول', 'Rabi\'al-thani': 'ربيع الثاني', 'Jumada al-awwal': 'جمادى الأولى', 'Jumada al-thani': 'جمادى الثانية', 'Rajab': 'رجب', 'Sha\'ban': 'شعبان', 'Ramadan': 'رمضان', 'Shawwal': 'شوال', 'Dhu al-Qi\'dah': 'ذو القعدة', 'Dhu al-Hijjah': 'ذو الحجة'},
        'language': 'اللغة',
        'settings': 'الإعدادات',
        'prayers': {
            'Date': 'التاريخ',
            'Fajr': 'الفجر',
            'Sunrise': 'الشروق',
            'Dohr': 'الظهر',
            'Asr': 'العصر',
            'Maghreb': 'المغرب',
            'Isha': 'العشاء'
        }
    },
    'fr': {
        'app_title': 'Horaires de Priere',
        'next_prayer': 'PROCHAINE PRIERE',
        'tomorrow': 'Demain',
        'loading': '🔄 Chargement des horaires de priere...',
        'refresh': '↻ Actualiser',
        'error': '⚠️ Erreur: {}\n\nVeuillez verifier votre connexion Internet\net reessayer.',
        'welcome': '🕌 Bienvenue dans Horaires de Priere',
        'select_city': 'Veuillez selectionner votre ville par defaut pour les horaires de priere:',
        'search_city': 'Rechercher une ville...',
        'cancel': 'Annuler',
        'set_default': 'Definir par defaut',
        'change_city': 'Changer la ville par defaut',
        'iqama_time': 'Temps avant Iqama de {}: {:02d}:{:02d}:{:02d}',
        'iqama_passed': 'Iqama de {}: 00:00:00',
        'hijri_unavailable': 'Date hijri non disponible',
        'hijri_approx': '{} AH (Approximatif)',
        'morocco': 'Maroc',
        'months': ['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre'],
        'days': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'],
        'hijri_months': {'Muharram': 'Muharram', 'Safar': 'Safar', 'Rabi\'al-awwal': 'Rabi al-Awwal', 'Rabi\'al-thani': 'Rabi al-Thani', 'Jumada al-awwal': 'Jumada al-Awwal', 'Jumada al-thani': 'Jumada al-Thani', 'Rajab': 'Rajab', 'Sha\'ban': 'Shaban', 'Ramadan': 'Ramadan', 'Shawwal': 'Shawwal', 'Dhu al-Qi\'dah': 'Dhu al-Qidah', 'Dhu al-Hijjah': 'Dhu al-Hijjah'},
        'language': 'Langue',
        'settings': 'Parametres',
        'prayers': {
            'Date': 'Date',
            'Fajr': 'Fajr',
            'Sunrise': 'Lever du soleil',
            'Dohr': 'Dhuhr',
            'Asr': 'Asr',
            'Maghreb': 'Maghrib',
            'Isha': 'Isha'
        }
    }
}

CITIES = {
    'Tangier': {'id': 101, 'en': 'Tangier', 'ar': 'طنجة', 'fr': 'Tanger'},
    'Casablanca': {'id': 71, 'en': 'Casablanca', 'ar': 'الدار البيضاء', 'fr': 'Casablanca'},
    'Rabat': {'id': 95, 'en': 'Rabat', 'ar': 'الرباط', 'fr': 'Rabat'},
    'Marrakech': {'id': 88, 'en': 'Marrakech', 'ar': 'مراكش', 'fr': 'Marrakech'},
    'Fes': {'id': 78, 'en': 'Fes', 'ar': 'فاس', 'fr': 'Fes'},
    'Agadir': {'id': 66, 'en': 'Agadir', 'ar': 'أكادير', 'fr': 'Agadir'},
    'Meknes': {'id': 89, 'en': 'Meknes', 'ar': 'مكناس', 'fr': 'Meknes'},
    'Oujda': {'id': 93, 'en': 'Oujda', 'ar': 'وجدة', 'fr': 'Oujda'},
    'Kenitra': {'id': 81, 'en': 'Kenitra', 'ar': 'القنيطرة', 'fr': 'Kenitra'},
    'Tetouan': {'id': 100, 'en': 'Tetouan', 'ar': 'تطوان', 'fr': 'Tetouan'},
    'Safi': {'id': 96, 'en': 'Safi', 'ar': 'آسفي', 'fr': 'Safi'},
    'Mohammedia': {'id': 90, 'en': 'Mohammedia', 'ar': 'المحمدية', 'fr': 'Mohammedia'},
    'Khouribga': {'id': 83, 'en': 'Khouribga', 'ar': 'خريبكة', 'fr': 'Khouribga'},
    'El Jadida': {'id': 74, 'en': 'El Jadida', 'ar': 'الجديدة', 'fr': 'El Jadida'},
    'Taza': {'id': 105, 'en': 'Taza', 'ar': 'تازة', 'fr': 'Taza'},
    'Nador': {'id': 91, 'en': 'Nador', 'ar': 'الناظور', 'fr': 'Nador'},
    'Settat': {'id': 98, 'en': 'Settat', 'ar': 'سطات', 'fr': 'Settat'},
    'Larache': {'id': 87, 'en': 'Larache', 'ar': 'العرائش', 'fr': 'Larache'},
    'Khenifra': {'id': 82, 'en': 'Khenifra', 'ar': 'خنيفرة', 'fr': 'Khenifra'},
    'Essaouira': {'id': 76, 'en': 'Essaouira', 'ar': 'الصويرة', 'fr': 'Essaouira'},
    'Chefchaouen': {'id': 72, 'en': 'Chefchaouen', 'ar': 'شفشاون', 'fr': 'Chefchaouen'},
    'Beni Mellal': {'id': 68, 'en': 'Beni Mellal', 'ar': 'بني ملال', 'fr': 'Beni Mellal'},
    'Al Hoceima': {'id': 79, 'en': 'Al Hoceima', 'ar': 'الحسيمة', 'fr': 'Al Hoceima'},
    'Taroudant': {'id': 103, 'en': 'Taroudant', 'ar': 'تارودانت', 'fr': 'Taroudant'},
    'Ouazzane': {'id': 92, 'en': 'Ouazzane', 'ar': 'وزان', 'fr': 'Ouazzane'},
    'Sefrou': {'id': 97, 'en': 'Sefrou', 'ar': 'صفرو', 'fr': 'Sefrou'},
    'Berkane': {'id': 69, 'en': 'Berkane', 'ar': 'بركان', 'fr': 'Berkane'},
    'Errachidia': {'id': 75, 'en': 'Errachidia', 'ar': 'الراشيدية', 'fr': 'Errachidia'},
    'Laayoune': {'id': 85, 'en': 'Laayoune', 'ar': 'العيون', 'fr': 'Laayoune'},
    'Tiznit': {'id': 106, 'en': 'Tiznit', 'ar': 'تزنيت', 'fr': 'Tiznit'},
    'Ifrane': {'id': 80, 'en': 'Ifrane', 'ar': 'إفران', 'fr': 'Ifrane'},
    'Zagora': {'id': 107, 'en': 'Zagora', 'ar': 'زاكورة', 'fr': 'Zagora'},
    'Dakhla': {'id': 73, 'en': 'Dakhla', 'ar': 'الداخلة', 'fr': 'Dakhla'},
    'Tan Tan': {'id': 102, 'en': 'Tan Tan', 'ar': 'طانطان', 'fr': 'Tan-Tan'},
    'Sidi Kacem': {'id': 99, 'en': 'Sidi Kacem', 'ar': 'سيدي قاسم', 'fr': 'Sidi Kacem'},
    'Ksar Lekbir': {'id': 84, 'en': 'Ksar Lekbir', 'ar': 'القصر الكبير', 'fr': 'Ksar el-Kebir'},
    'Taounate': {'id': 104, 'en': 'Taounate', 'ar': 'تاونات', 'fr': 'Taounate'},
    'Assila': {'id': 67, 'en': 'Assila', 'ar': 'أصيلة', 'fr': 'Asilah'},
    'Boulemane': {'id': 70, 'en': 'Boulemane', 'ar': 'بولمان', 'fr': 'Boulemane'},
    'Kalaat Sraghna': {'id': 94, 'en': 'Kalaat Sraghna', 'ar': 'قلعة السراغنة', 'fr': 'Kalaat es-Sraghna'},
    'Lagouira': {'id': 86, 'en': 'Lagouira', 'ar': 'الكويرة', 'fr': 'Lagouira'},
    'Moulay Idriss Zerhoun': {'id': 108, 'en': 'Moulay Idriss Zerhoun', 'ar': 'مولاي إدريس زرهون', 'fr': 'Moulay Idriss Zerhoun'},
    'Smara': {'id': 77, 'en': 'Smara', 'ar': 'السمارة', 'fr': 'Smara'}
}

class SettingsDialog(QDialog):
    def __init__(self, current_city, current_language, parent=None):
        super().__init__(parent)
        self.current_city = current_city
        self.current_language = current_language
        self.cities = sorted(CITIES.keys())
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(self.tr('settings'))
        self.setFixedSize(400, 450)
        self.setModal(True)
        self.setStyleSheet('background-color: black; color: white;')
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel(self.tr('settings'))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 20px; font-weight: bold; color: white;')
        layout.addWidget(title)
        
        # Language selection
        lang_label = QLabel(self.tr('language') + ':')
        lang_label.setStyleSheet('font-size: 14px; color: #ccc;')
        layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(['English', 'العربية', 'Français'])
        lang_map = {'en': 0, 'ar': 1, 'fr': 2}
        self.language_combo.setCurrentIndex(lang_map.get(self.current_language, 0))
        self.language_combo.setStyleSheet('''
            QComboBox {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #444;
                border-radius: 8px;
                background-color: #333;
                color: white;
            }
        ''')
        layout.addWidget(self.language_combo)
        
        # City selection
        city_label = QLabel(self.tr('select_city'))
        city_label.setStyleSheet('font-size: 14px; color: #ccc;')
        layout.addWidget(city_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr('search_city'))
        self.search_box.textChanged.connect(self.filter_cities)
        self.search_box.setStyleSheet('''
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #444;
                border-radius: 8px;
                background-color: #333;
                color: white;
            }
            QLineEdit:focus {
                border-color: #2d5a27;
            }
        ''')
        layout.addWidget(self.search_box)
        
        self.city_list = QListWidget()
        translated_cities = self.get_translated_cities()
        self.city_list.addItems(translated_cities)
        current_translated = CITIES[self.current_city][self.current_language]
        try:
            self.city_list.setCurrentRow(translated_cities.index(current_translated))
        except ValueError:
            self.city_list.setCurrentRow(0)
        self.city_list.setFixedHeight(120)
        self.city_list.setStyleSheet('''
            QListWidget {
                background-color: #333;
                border: 2px solid #444;
                border-radius: 8px;
                color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #2d5a27;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #555;
            }
        ''')
        layout.addWidget(self.city_list)
        
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton(self.tr('cancel'))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet('padding: 10px 20px; background: #666; color: white; border: none; border-radius: 6px;')
        
        ok_btn = QPushButton(self.tr('set_default'))
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet('padding: 10px 20px; background: #2d5a27; color: white; border: none; border-radius: 6px; font-weight: bold;')
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)
        
    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)
        
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
        self.setWindowTitle('Select Your Default City')
        self.setFixedSize(400, 350)
        self.setModal(True)
        self.setStyleSheet('background-color: black; color: white;')
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel(self.tr('welcome'))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 20px; font-weight: bold; color: white;')
        layout.addWidget(title)
        
        subtitle = QLabel(self.tr('select_city'))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet('font-size: 14px; color: #ccc;')
        layout.addWidget(subtitle)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr('search_city'))
        self.search_box.textChanged.connect(self.filter_cities)
        self.search_box.setStyleSheet('''
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #444;
                border-radius: 8px;
                background-color: #333;
                color: white;
            }
            QLineEdit:focus {
                border-color: #2d5a27;
            }
        ''')
        layout.addWidget(self.search_box)
        
        # City list
        self.city_list = QListWidget()
        translated_cities = self.get_translated_cities()
        self.city_list.addItems(translated_cities)
        tangier_translated = CITIES['Tangier'][self.language]
        try:
            self.city_list.setCurrentRow(translated_cities.index(tangier_translated))
        except ValueError:
            self.city_list.setCurrentRow(0)
        self.city_list.setFixedHeight(150)
        self.city_list.setStyleSheet('''
            QListWidget {
                background-color: #333;
                border: 2px solid #444;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                max-height: 150px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #2d5a27;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #555;
            }
            QScrollBar:vertical {
                background-color: #444;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #666;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #888;
            }
        ''')
        layout.addWidget(self.city_list)
        
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton(self.tr('cancel'))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet('padding: 10px 20px; background: #666; color: white; border: none; border-radius: 6px;')
        
        ok_btn = QPushButton(self.tr('set_default'))
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet('padding: 10px 20px; background: #2d5a27; color: white; border: none; border-radius: 6px; font-weight: bold;')
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)
        
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

class PrayerTimeWorker(QThread):
    data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, city_id=101):
        super().__init__()
        self.city_id = city_id
    
    def run(self):
        try:
            url = f'https://www.yabiladi.com/prieres/details/{self.city_id}/city.html'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            prayer_table = soup.find('table')
            
            if not prayer_table:
                raise Exception("Prayer table not found")
            
            headers = [header.text.strip() for header in prayer_table.find_all('th')]
            rows = prayer_table.find_all('tr')[1:]
            
            today = datetime.now().strftime('%d/%m')
            todays_prayers = None
            
            for row in rows:
                columns = row.find_all('td')
                if columns:
                    date = columns[0].text.strip()
                    if date == today:
                        todays_prayers = [col.text.strip() for col in columns]
                        break
            
            if todays_prayers:
                prayer_times = {}
                for header, time in zip(headers, todays_prayers):
                    prayer_times[header] = time
                self.data_received.emit(prayer_times)
            else:
                self.error_occurred.emit("No prayer times found for today")
                
        except Exception as e:
            self.error_occurred.emit(str(e))

class ModernSalahApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.prayer_times = {}
        self.current_prayer = None
        self.config_file = os.path.expanduser('~/.salah_config.json')
        self.current_language = self.load_language_config()
        self.current_city = self.load_city_config()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # Update every second
        
        self.init_ui()
        self.update_all_ui_text()
        self.load_prayer_times()
        
    def load_language_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('language', 'en')
            except:
                pass
        return 'en'
    
    def load_city_config(self):
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
                self.current_city = new_city
                self.current_language = new_language
                self.save_config(new_city, new_language)
                self.update_ui_language()
                if new_city != self.current_city:
                    self.prayer_times = {}
                    self.load_prayer_times()
        
    def init_ui(self):
        self.setWindowTitle('🕌 Salah Times - Tangier')
        self.setFixedSize(400, 700)
        self.setStyleSheet(self.get_stylesheet())
        
        # Center window
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Content area
        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Date section
        date_card = self.create_date_card()
        content_layout.addWidget(date_card)
        
        # Prayer times section
        self.prayer_card = self.create_prayer_card()
        content_layout.addWidget(self.prayer_card)
        
        # Next prayer section
        self.next_prayer_card = self.create_next_prayer_card()
        content_layout.addWidget(self.next_prayer_card)
        
        # Refresh button
        refresh_btn = self.create_refresh_button()
        content_layout.addWidget(refresh_btn)
        
        layout.addWidget(content)
        
    def get_stylesheet(self):
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fffe, stop:1 #e8f5e8);
            }
            
            #header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d5a27, stop:1 #4a7c59);
                border: none;
            }
            
            #header QLabel {
                color: white;
                border: none;
            }
            
            #mosque_icon {
                font-size: 32px;
                font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", Arial;
            }
            
            #title {
                font-size: 24px;
                font-weight: bold;
                font-family: 'Inter', sans-serif;
            }
            
            #location {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.9);
                font-family: 'Inter', sans-serif;
            }
            
            #content {
                background: transparent;
            }
            
            .card {
                background: white;
                border-radius: 16px;
                border: none;
                padding: 30px;
                height: 350px;
            }
            
            .date_card {
                background: white;
                border-radius: 16px;
                border: none;
                padding: 12px;
                min-height: 60px;
            }
            
            .date_card QLabel {
                color: #2d5a27;
                border: none;
                background: transparent;
            }
            
            #hijri_date {
                font-size: 18px;
                font-weight: bold;
                color: #2d5a27;
                font-family: 'Inter', sans-serif;
            }
            
            #current_date {
                font-size: 14px;
                color: #666666;
                font-family: 'Inter', sans-serif;
            }
            
            .prayer_item {
                background: transparent;
                border: none;
                padding: 16px 0px;
                border-bottom: 1px solid #f0f0f0;
            }
            
            .prayer_item:last-child {
                border-bottom: none;
            }
            
            .prayer_item.current {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(74, 124, 89, 0.1), stop:1 rgba(74, 124, 89, 0.05));
                border-radius: 12px;
                padding: 16px;
                margin: 0px -16px;
                border-bottom: 1px solid rgba(74, 124, 89, 0.2);
            }
            
            .prayer_name {
                font-size: 16px;
                font-weight: bold;
                color: #2d5a27;
                font-family: 'Inter', sans-serif;
                background: transparent;
                border: none;
            }
            
            .prayer_time {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                font-family: 'Inter', sans-serif;
                background: transparent;
                border: none;
            }
            
            .prayer_icon {
                font-size: 24px;
                font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", Arial;
                background: transparent;
                border: none;
                min-width: 30px;
            }
            
            .next_prayer_card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4a7c59, stop:1 #2d5a27);
                border-radius: 16px;
                border: none;
                padding: 20px;
            }
            
            .next_prayer_card QLabel {
                color: white;
                background: transparent;
                border: none;
                font-family: 'Inter', sans-serif;
            }
            
            #next_label {
                font-size: 12px;
                color: rgba(255, 255, 255, 0.8);
                font-weight: bold;
            }
            
            #next_name {
                font-size: 20px;
                font-weight: bold;
            }
            
            #next_time {
                font-size: 16px;
                color: rgba(255, 255, 255, 0.9);
            }
            
            #countdown {
                font-size: 24px;
                font-weight: bold;
            }
            
            #iqama_countdown {
                font-size: 18px;
                font-weight: bold;
                color: #ff4444;
            }
            
            #refresh_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4a7c59, stop:1 #2d5a27);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 20px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Inter', sans-serif;
            }
            
            #refresh_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a8c69, stop:1 #3d6a37);
            }
            
            #refresh_btn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1d4a17, stop:1 #2d5a27);
            }
            
            #settings_btn {
                background: transparent;
                border: none;
                font-size: 16px;
                color: rgba(255, 255, 255, 0.8);
            }
            
            #settings_btn:hover {
                color: white;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
            
            .loading {
                color: #666666;
                font-size: 14px;
                font-family: 'Inter', sans-serif;
                background: transparent;
                border: none;
            }
            
            .error {
                color: #d32f2f;
                font-size: 12px;
                font-family: 'Inter', sans-serif;
                background: transparent;
                border: none;
            }
        """
        
    def create_header(self):
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(150)
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(20, 25, 20, 25)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)
        
        mosque_icon = QLabel("🕌")
        mosque_icon.setObjectName("mosque_icon")
        mosque_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(mosque_icon)
        
        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        self.location_label = QLabel()
        self.location_label.setObjectName("location")
        self.location_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.location_label)
        
        settings_btn = QPushButton("⚙️")
        settings_btn.setObjectName("settings_btn")
        settings_btn.clicked.connect(self.show_settings)
        settings_btn.setFixedSize(30, 30)
        settings_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(settings_btn)
        
        return header
        
    def create_date_card(self):
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
        self.prayer_layout.setContentsMargins(20, 20, 20, 20)
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
        # Clear current prayer times display
        self.clear_prayer_layout()
        loading = QLabel("🔄 Loading prayer times...")
        loading.setProperty("class", "loading")
        loading.setAlignment(Qt.AlignCenter)
        self.prayer_layout.addWidget(loading)
        
        # Start worker thread
        city_id = CITIES.get(self.current_city, {'id': 101})['id']
        self.worker = PrayerTimeWorker(city_id)
        self.worker.data_received.connect(self.display_prayer_times)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.start()
        
    def clear_prayer_layout(self):
        while self.prayer_layout.count():
            child = self.prayer_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def display_prayer_times(self, prayer_times):
        self.prayer_times = prayer_times
        self.clear_prayer_layout()
        
        icons = {'Date': '📅', 'Fajr': '🌌', 'Sunrise': '🌞', 'Dohr': '🔆', 
                'Asr': '🌅', 'Maghreb': '🌇', 'Isha': '🌃'}
        
        current_prayer = self.get_current_prayer()
        
        for header, time in prayer_times.items():
            item = QWidget()
            item.setProperty("class", "prayer_item")
            if header == current_prayer:
                item.setProperty("class", "prayer_item current")
            
            layout = QHBoxLayout(item)
            layout.setContentsMargins(0, 0, 0, 0)
            
            icon = QLabel(icons.get(header, '🕐'))
            icon.setStyleSheet("font-size: 24px; font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', Arial; min-width: 30px;")
            layout.addWidget(icon)
            
            translated_name = self.tr_prayer(header)
            name = QLabel(translated_name)
            name.setProperty("class", "prayer_name")
            layout.addWidget(name)
            
            layout.addStretch()
            
            time_label = QLabel(time)
            time_label.setProperty("class", "prayer_time")
            layout.addWidget(time_label)
            
            self.prayer_layout.addWidget(item)
        
        self.update_next_prayer()
        self.update_countdown()
    
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
        self.update_location_label()
        self.update_dates()
    
    def update_ui_language(self):
        self.update_all_ui_text()
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
        
        if prayers:
            first_prayer = prayers[0]
            self.next_name.setText(f"{self.tr_prayer(first_prayer)} ({self.tr('tomorrow')})")
            self.next_time.setText(self.prayer_times[first_prayer])
            
    def get_iqama_delay(self, prayer):
        delays = {'Fajr': 20, 'Dohr': 15, 'Asr': 15, 'Maghreb': 10, 'Isha': 15}
        return delays.get(prayer, 0)
    
    def is_iqama_time(self, prayer):
        if not prayer or prayer not in self.prayer_times:
            return False
        
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        prayer_time = self.parse_time(self.prayer_times[prayer])
        iqama_delay = self.get_iqama_delay(prayer)
        
        return prayer_time <= current_time < prayer_time + iqama_delay
    
    def update_countdown(self):
        if not self.prayer_times:
            return
            
        now = datetime.now()
        current_time = now.hour * 60 + now.minute
        current_seconds = now.second
        
        prayers = [name for name in self.prayer_times.keys() if name != 'Date']
        
        # Always show Iqama countdown for current prayer
        current_prayer = self.get_current_prayer()
        if current_prayer:
            prayer_time = self.parse_time(self.prayer_times[current_prayer])
            iqama_delay = self.get_iqama_delay(current_prayer)
            iqama_end_time = prayer_time + iqama_delay
            
            remaining = iqama_end_time - current_time
            
            if remaining <= 0:
                self.iqama_countdown.setText(self.tr('iqama_passed').format(self.tr_prayer(current_prayer)))
                self.iqama_countdown.setStyleSheet("color: #90EE90; font-weight: bold;")
            else:
                hours = remaining // 60
                minutes = remaining % 60
                seconds = 60 - current_seconds if current_seconds > 0 else 0
                
                if seconds == 60:
                    seconds = 0
                elif seconds > 0 and minutes > 0:
                    minutes -= 1
                
                self.iqama_countdown.setText(self.tr('iqama_time').format(self.tr_prayer(current_prayer), hours, minutes, seconds))
                self.iqama_countdown.setStyleSheet("color: #90EE90; font-weight: bold;")
        else:
            self.iqama_countdown.setText("")
        
        # Regular next prayer countdown
        next_prayer_time = None
        
        for prayer in prayers:
            if prayer in self.prayer_times:
                prayer_time = self.parse_time(self.prayer_times[prayer])
                if prayer_time > current_time:
                    next_prayer_time = prayer_time
                    break
        
        if not next_prayer_time and prayers:
            first_prayer = prayers[0]  # This should be Fajr
            fajr_time = self.parse_time(self.prayer_times[first_prayer])
            # Calculate minutes until tomorrow's Fajr
            minutes_until_midnight = (24 * 60) - current_time
            remaining = minutes_until_midnight + fajr_time
        else:
            remaining = next_prayer_time - current_time if next_prayer_time else 0
        
        if next_prayer_time or remaining > 0:
            
            hours = remaining // 60
            minutes = remaining % 60
            seconds = 60 - current_seconds if current_seconds > 0 else 0
            
            if seconds == 60:
                seconds = 0
            elif seconds > 0:
                if minutes > 0:
                    minutes -= 1
                elif hours > 0:
                    hours -= 1
                    minutes = 59
            
            self.countdown.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
    def show_error(self, error_message):
        self.clear_prayer_layout()
        error = QLabel(f"⚠️ Error: {error_message}\n\nPlease check your internet connection\nand try refreshing.")
        error.setProperty("class", "error")
        error.setAlignment(Qt.AlignCenter)
        error.setWordWrap(True)
        self.prayer_layout.addWidget(error)

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Salah Times")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Islamic Apps")
    
    window = ModernSalahApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()