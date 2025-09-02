#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import threading
import json
import os
import subprocess
import math

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
            'Chorok': 'Sunrise',
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
            'Chorok': 'الشروق',
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
            'Chorok': 'Lever du soleil',
            'Dohr': 'Dhuhr',
            'Asr': 'Asr',
            'Maghreb': 'Maghrib',
            'Isha': 'Isha'
        }
    }
}

CITIES = {
    'Tangier': {'id': 101, 'en': 'Tangier', 'ar': 'طنجة', 'fr': 'Tanger', 'lat': 35.7595, 'lon': -5.8340},
    'Casablanca': {'id': 71, 'en': 'Casablanca', 'ar': 'الدار البيضاء', 'fr': 'Casablanca', 'lat': 33.5731, 'lon': -7.5898},
    'Rabat': {'id': 95, 'en': 'Rabat', 'ar': 'الرباط', 'fr': 'Rabat', 'lat': 34.0209, 'lon': -6.8416},
    'Marrakech': {'id': 88, 'en': 'Marrakech', 'ar': 'مراكش', 'fr': 'Marrakech', 'lat': 31.6295, 'lon': -7.9811},
    'Fes': {'id': 78, 'en': 'Fes', 'ar': 'فاس', 'fr': 'Fes', 'lat': 34.0181, 'lon': -5.0078},
    'Agadir': {'id': 66, 'en': 'Agadir', 'ar': 'أكادير', 'fr': 'Agadir', 'lat': 30.4278, 'lon': -9.5981},
    'Meknes': {'id': 89, 'en': 'Meknes', 'ar': 'مكناس', 'fr': 'Meknes', 'lat': 33.8935, 'lon': -5.5473},
    'Oujda': {'id': 93, 'en': 'Oujda', 'ar': 'وجدة', 'fr': 'Oujda', 'lat': 34.6814, 'lon': -1.9086},
    'Kenitra': {'id': 81, 'en': 'Kenitra', 'ar': 'القنيطرة', 'fr': 'Kenitra', 'lat': 34.2610, 'lon': -6.5802},
    'Tetouan': {'id': 100, 'en': 'Tetouan', 'ar': 'تطوان', 'fr': 'Tetouan', 'lat': 35.5889, 'lon': -5.3626},
    'Safi': {'id': 96, 'en': 'Safi', 'ar': 'آسفي', 'fr': 'Safi', 'lat': 32.2994, 'lon': -9.2372},
    'Mohammedia': {'id': 90, 'en': 'Mohammedia', 'ar': 'المحمدية', 'fr': 'Mohammedia', 'lat': 33.6866, 'lon': -7.3837},
    'Khouribga': {'id': 83, 'en': 'Khouribga', 'ar': 'خريبكة', 'fr': 'Khouribga', 'lat': 32.8811, 'lon': -6.9063},
    'El Jadida': {'id': 74, 'en': 'El Jadida', 'ar': 'الجديدة', 'fr': 'El Jadida', 'lat': 33.2316, 'lon': -8.5007},
    'Taza': {'id': 105, 'en': 'Taza', 'ar': 'تازة', 'fr': 'Taza', 'lat': 34.2133, 'lon': -4.0103},
    'Nador': {'id': 91, 'en': 'Nador', 'ar': 'الناظور', 'fr': 'Nador', 'lat': 35.1681, 'lon': -2.9287},
    'Settat': {'id': 98, 'en': 'Settat', 'ar': 'سطات', 'fr': 'Settat', 'lat': 33.0018, 'lon': -7.6164},
    'Larache': {'id': 87, 'en': 'Larache', 'ar': 'العرائش', 'fr': 'Larache', 'lat': 35.1932, 'lon': -6.1563},
    'Khenifra': {'id': 82, 'en': 'Khenifra', 'ar': 'خنيفرة', 'fr': 'Khenifra', 'lat': 32.9359, 'lon': -5.6675},
    'Essaouira': {'id': 76, 'en': 'Essaouira', 'ar': 'الصويرة', 'fr': 'Essaouira', 'lat': 31.5085, 'lon': -9.7595},
    'Chefchaouen': {'id': 72, 'en': 'Chefchaouen', 'ar': 'شفشاون', 'fr': 'Chefchaouen', 'lat': 35.1688, 'lon': -5.2636},
    'Beni Mellal': {'id': 68, 'en': 'Beni Mellal', 'ar': 'بني ملال', 'fr': 'Beni Mellal', 'lat': 32.3373, 'lon': -6.3498},
    'Al Hoceima': {'id': 79, 'en': 'Al Hoceima', 'ar': 'الحسيمة', 'fr': 'Al Hoceima', 'lat': 35.2517, 'lon': -3.9316},
    'Taroudant': {'id': 103, 'en': 'Taroudant', 'ar': 'تارودانت', 'fr': 'Taroudant', 'lat': 30.4703, 'lon': -8.8770},
    'Ouazzane': {'id': 92, 'en': 'Ouazzane', 'ar': 'وزان', 'fr': 'Ouazzane', 'lat': 34.7936, 'lon': -5.5836},
    'Sefrou': {'id': 97, 'en': 'Sefrou', 'ar': 'صفرو', 'fr': 'Sefrou', 'lat': 33.8307, 'lon': -4.8372},
    'Berkane': {'id': 69, 'en': 'Berkane', 'ar': 'بركان', 'fr': 'Berkane', 'lat': 34.9218, 'lon': -2.3200},
    'Errachidia': {'id': 75, 'en': 'Errachidia', 'ar': 'الراشيدية', 'fr': 'Errachidia', 'lat': 31.9314, 'lon': -4.4244},
    'Laayoune': {'id': 85, 'en': 'Laayoune', 'ar': 'العيون', 'fr': 'Laayoune', 'lat': 27.1253, 'lon': -13.1625},
    'Tiznit': {'id': 106, 'en': 'Tiznit', 'ar': 'تزنيت', 'fr': 'Tiznit', 'lat': 29.6974, 'lon': -9.7316},
    'Ifrane': {'id': 80, 'en': 'Ifrane', 'ar': 'إفران', 'fr': 'Ifrane', 'lat': 33.5228, 'lon': -5.1106},
    'Zagora': {'id': 107, 'en': 'Zagora', 'ar': 'زاكورة', 'fr': 'Zagora', 'lat': 30.3314, 'lon': -5.8372},
    'Dakhla': {'id': 73, 'en': 'Dakhla', 'ar': 'الداخلة', 'fr': 'Dakhla', 'lat': 23.6848, 'lon': -15.9570},
    'Tan Tan': {'id': 102, 'en': 'Tan Tan', 'ar': 'طانطان', 'fr': 'Tan-Tan', 'lat': 28.4378, 'lon': -11.1031},
    'Sidi Kacem': {'id': 99, 'en': 'Sidi Kacem', 'ar': 'سيدي قاسم', 'fr': 'Sidi Kacem', 'lat': 34.2214, 'lon': -5.7081},
    'Ksar Lekbir': {'id': 84, 'en': 'Ksar Lekbir', 'ar': 'القصر الكبير', 'fr': 'Ksar el-Kebir', 'lat': 35.0119, 'lon': -5.9033},
    'Taounate': {'id': 104, 'en': 'Taounate', 'ar': 'تاونات', 'fr': 'Taounate', 'lat': 34.5386, 'lon': -4.6372},
    'Assila': {'id': 67, 'en': 'Assila', 'ar': 'أصيلة', 'fr': 'Asilah', 'lat': 35.4650, 'lon': -6.0362},
    'Boulemane': {'id': 70, 'en': 'Boulemane', 'ar': 'بولمان', 'fr': 'Boulemane', 'lat': 33.3614, 'lon': -4.7331},
    'Kalaat Sraghna': {'id': 94, 'en': 'Kalaat Sraghna', 'ar': 'قلعة السراغنة', 'fr': 'Kalaat es-Sraghna', 'lat': 32.0587, 'lon': -7.4103},
    'Lagouira': {'id': 86, 'en': 'Lagouira', 'ar': 'الكويرة', 'fr': 'Lagouira', 'lat': 20.9331, 'lon': -17.0439},
    'Moulay Idriss Zerhoun': {'id': 108, 'en': 'Moulay Idriss Zerhoun', 'ar': 'مولاي إدريس زرهون', 'fr': 'Moulay Idriss Zerhoun', 'lat': 34.0581, 'lon': -5.5203},
    'Smara': {'id': 77, 'en': 'Smara', 'ar': 'السمارة', 'fr': 'Smara', 'lat': 26.7386, 'lon': -11.6719}
}

class SettingsDialog(QDialog):
    def __init__(self, current_city, current_language, parent=None):
        super().__init__(parent)
        self.current_city = current_city
        self.current_language = current_language
        self.cities = sorted(CITIES.keys())
        self.config_dir = os.path.join(os.path.expanduser('~'), '.salah_times', 'config')
        self.geometry_file = os.path.join(self.config_dir, 'settings_geometry.json')
        self.iqama_config_file = os.path.join(self.config_dir, 'iqama_times.json')
        self.iqama_times = self.load_iqama_times()
        self.init_ui()
        self.restore_geometry()
        
    def init_ui(self):
        self.setWindowTitle(self.tr('settings'))
        self.setMinimumSize(500, 600)
        self.resize(500, 650)
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
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 14px;
                font-weight: 500;
                color: #666;
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
                padding: 8px 12px;
                font-size: 14px;
                color: #333;
                max-width: 80px;
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
        
        # Iqama times card
        iqama_card = QWidget()
        iqama_card.setProperty("class", "settings_card")
        
        card_layout = QVBoxLayout(iqama_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(15)
        
        # Title
        title = QLabel("Configure Iqama Delay Times")
        title.setProperty("class", "section_label")
        title.setWordWrap(True)
        card_layout.addWidget(title)
        
        # Description
        desc = QLabel("Set the delay time (in minutes) between Adhan and Iqama for each prayer:")
        desc.setStyleSheet("color: #666; font-size: 12px;")
        desc.setWordWrap(True)
        card_layout.addWidget(desc)
        
        # Iqama inputs
        self.iqama_inputs = {}
        prayers = ['Fajr', 'Dohr', 'Asr', 'Maghreb', 'Isha']
        icons = {'Fajr': '🌌', 'Dohr': '🔆', 'Asr': '🌅', 'Maghreb': '🌇', 'Isha': '🌃'}
        
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
        
        layout.addWidget(iqama_card)
        
        # Reset button
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.setProperty("class", "cancel_button")
        reset_btn.clicked.connect(self.reset_iqama_times)
        reset_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        
        return tab
    
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
        super().accept()
    
    def closeEvent(self, event):
        """Save geometry when dialog closes"""
        self.save_geometry()
        super().closeEvent(event)
        
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

class OfflineSunriseCalculator:
    @staticmethod
    def calculate_sunrise(city_name, date):
        """Calculate sunrise time offline using astronomical formulas"""
        try:
            if city_name not in CITIES or 'lat' not in CITIES[city_name]:
                print(f"Debug: City {city_name} not found or no coordinates")
                return None
            
            lat = CITIES[city_name]['lat']
            lon = CITIES[city_name]['lon']
            print(f"Debug: Calculating for {city_name} at {lat}, {lon}")
            
            # Get day of year
            day_of_year = date.timetuple().tm_yday
            print(f"Debug: Day of year: {day_of_year}")
            
            # Calculate solar declination (δ)
            declination = 23.44 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
            print(f"Debug: Declination: {declination}")
            
            # Convert latitude to radians
            lat_rad = math.radians(lat)
            decl_rad = math.radians(declination)
            
            # Calculate hour angle (ω) for sunrise
            cos_hour_angle = -math.tan(lat_rad) * math.tan(decl_rad)
            print(f"Debug: cos_hour_angle: {cos_hour_angle}")
            
            # Check if sun rises (polar regions might not have sunrise/sunset)
            if cos_hour_angle < -1 or cos_hour_angle > 1:
                print(f"Debug: No sunrise/sunset for this location and date")
                return None
                
            hour_angle = math.degrees(math.acos(cos_hour_angle))
            print(f"Debug: Hour angle: {hour_angle}")
            
            # Morocco timezone offset (UTC+1, no DST)
            timezone_offset = 1
            
            # Compute solar noon
            solar_noon = 12 - (lon / 15 - timezone_offset)
            print(f"Debug: Solar noon: {solar_noon}")
            
            # Compute sunrise time
            sunrise_time = solar_noon - (hour_angle / 15)
            print(f"Debug: Sunrise time (decimal): {sunrise_time}")
            
            # Convert to hours and minutes
            hours = int(sunrise_time)
            minutes = int((sunrise_time - hours) * 60)
            
            # Handle negative hours (previous day)
            if hours < 0:
                hours += 24
            
            # Ensure valid time format
            hours = hours % 24
            minutes = max(0, min(59, minutes))
            
            result = f"{hours:02d}:{minutes:02d}"
            result = f"{hours:02d}:{minutes:02d}"
            print(f"Debug: Final sunrise time: {result}")
            return result
            
        except Exception as e:
            print(f"Debug: Error in calculation: {e}")
            return None
    
    @staticmethod
    def calculate_all_prayer_times(city_name, date):
        """Calculate all prayer times for a city and date"""
        sunrise = OfflineSunriseCalculator.calculate_sunrise(city_name, date)
        if not sunrise:
            return None
        
        # For now, return sunrise as Chorok
        # This can be extended to calculate other prayer times
        return {
            'Date': date.strftime('%d/%m'),
            'Sunrise': sunrise,
            # Other prayers would be calculated here
            # For now, we'll still use web scraping for full prayer times
        }

class PrayerTimeWorker(QThread):
    data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    offline_data_loaded = pyqtSignal(dict, int)  # prayer_times, days_remaining
    
    def __init__(self, city_id=101, city_name="Tangier"):
        super().__init__()
        self.city_id = city_id
        self.city_name = city_name
        self.data_folder = os.path.join(os.path.expanduser('~'), '.salah_times', 'cities')
        self.storage_file = os.path.join(self.data_folder, f'{city_name.lower()}.json')
    
    def run(self):
        # Always load cached data first (fast)
        self.load_cached_data_immediately()
        
        # Check if we need to update in background
        if self.should_update_data():
            self.update_data_in_background()
    
    def load_cached_data_immediately(self):
        """Load cached data instantly without waiting"""
        today = datetime.now().strftime('%d/%m')
        offline_data = self.load_offline_data()
        
        if offline_data and today in offline_data['prayer_times']:
            self.data_received.emit(offline_data['prayer_times'][today])
        else:
            # No cached data, force update
            self.force_update_data()
    
    def should_update_data(self):
        """Check if data needs updating based on last scrape time"""
        try:
            config_folder = os.path.join(os.path.expanduser('~'), '.salah_times', 'config')
            update_file = os.path.join(config_folder, 'last_update.json')
            if not os.path.exists(update_file):
                return True
            
            with open(update_file, 'r') as f:
                update_info = json.load(f)
            
            last_update = datetime.fromisoformat(update_info['last_update'])
            now = datetime.now()
            
            # Update if more than 1 day old
            return (now - last_update).days >= 1
        except:
            return True
    
    def update_data_in_background(self):
        """Update data in background without blocking UI"""
        if self.check_internet_connection():
            try:
                self.update_all_cities_data()
                self.save_update_timestamp()
            except Exception as e:
                print(f"Background update failed: {e}")
    
    def force_update_data(self):
        """Force update when no cached data exists"""
        if self.check_internet_connection():
            try:
                self.update_all_cities_data()
                self.save_update_timestamp()
                
                # Load today's data
                today = datetime.now().strftime('%d/%m')
                offline_data = self.load_offline_data()
                if offline_data and today in offline_data['prayer_times']:
                    self.data_received.emit(offline_data['prayer_times'][today])
                else:
                    self.error_occurred.emit("No prayer times found for today")
            except Exception as e:
                # Fallback to offline calculation
                self.try_offline_calculation()
        else:
            # No internet: try offline calculation
            self.try_offline_calculation()
    
    def try_offline_calculation(self):
        """Try to calculate prayer times offline"""
        try:
            today = datetime.now()
            calculated_times = OfflineSunriseCalculator.calculate_all_prayer_times(self.city_name, today)
            
            if calculated_times:
                # For now, we only have sunrise calculation
                # Show partial data with calculated sunrise
                partial_times = {
                    'Date': today.strftime('%d/%m'),
                    'Fajr': '--:--',
                    'Sunrise': calculated_times['Sunrise'],
                    'Dohr': '--:--',
                    'Asr': '--:--',
                    'Maghreb': '--:--',
                    'Isha': '--:--'
                }
                self.offline_data_loaded.emit(partial_times, 0)
            else:
                self.error_occurred.emit("No internet connection and calculation failed")
        except Exception as e:
            self.error_occurred.emit(f"Offline calculation error: {str(e)}")
    
    def save_update_timestamp(self):
        """Save when we last updated the data"""
        try:
            config_folder = os.path.join(os.path.expanduser('~'), '.salah_times', 'config')
            os.makedirs(config_folder, exist_ok=True)
            update_file = os.path.join(config_folder, 'last_update.json')
            
            update_info = {
                'last_update': datetime.now().isoformat(),
                'cities_updated': len(CITIES)
            }
            
            with open(update_file, 'w') as f:
                json.dump(update_info, f, indent=2)
        except Exception as e:
            print(f"Could not save update timestamp: {e}")
    
    def get_city_coordinates(self):
        """Get coordinates for current city"""
        city_data = CITIES.get(self.city_name, {})
        return city_data.get('lat'), city_data.get('lon')
    
    def check_internet_connection(self):
        try:
            response = requests.get('https://www.yabiladi.com', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def update_all_cities_data(self):
        """Update prayer times for all cities"""
        os.makedirs(self.data_folder, exist_ok=True)
        
        for city_name, city_data in CITIES.items():
            try:
                city_id = city_data['id']
                url = f'https://www.yabiladi.com/prieres/details/{city_id}/city.html'
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                prayer_table = soup.find('table')
                
                if prayer_table:
                    headers = [header.text.strip() for header in prayer_table.find_all('th')]
                    rows = prayer_table.find_all('tr')[1:]
                    
                    all_prayer_times = {}
                    for row in rows:
                        columns = row.find_all('td')
                        if columns:
                            date = columns[0].text.strip()
                            prayer_data = {}
                            for header, col in zip(headers, columns):
                                prayer_data[header] = col.text.strip()
                            all_prayer_times[date] = prayer_data
                    
                    # Save city data to cities subfolder
                    city_file = os.path.join(self.data_folder, f'{city_name.lower()}.json')
                    city_data_obj = {
                        'city': city_name,
                        'last_updated': datetime.now().isoformat(),
                        'prayer_times': all_prayer_times
                    }
                    
                    with open(city_file, 'w', encoding='utf-8') as f:
                        json.dump(city_data_obj, f, ensure_ascii=False, indent=2)
                        
            except Exception as e:
                print(f"Error updating {city_name}: {e}")
                continue
    
    def load_offline_mode(self, error_msg):
        """Load offline data or show error"""
        if not os.path.exists(self.data_folder):
            self.error_occurred.emit("No internet connection and no offline data available")
            return
            
        offline_data = self.load_offline_data()
        if offline_data:
            today = datetime.now().strftime('%d/%m')
            if today in offline_data['prayer_times']:
                days_remaining = self.calculate_days_remaining(offline_data['prayer_times'])
                self.offline_data_loaded.emit(offline_data['prayer_times'][today], days_remaining)
            else:
                self.error_occurred.emit(f"Offline mode: No data for today")
        else:
            self.error_occurred.emit("No internet connection and no offline data available")
    

    
    def load_offline_data(self):
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading offline data: {e}")
        return None
    
    def calculate_days_remaining(self, prayer_times):
        try:
            today = datetime.now()
            dates = list(prayer_times.keys())
            
            # Convert dates to datetime objects for comparison
            date_objects = []
            for date_str in dates:
                try:
                    day, month = map(int, date_str.split('/'))
                    year = today.year
                    # Handle year transition
                    if month < today.month or (month == today.month and day < today.day):
                        year += 1
                    date_objects.append(datetime(year, month, day))
                except:
                    continue
            
            if date_objects:
                last_date = max(date_objects)
                days_remaining = (last_date - today).days + 1
                return max(0, days_remaining)
        except:
            pass
        return 0

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
        self.ensure_iqama_config_exists()
        self.current_language = self.load_language_config()
        self.current_city = self.load_city_config()
        self.tray_process = None
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # Update every second
        
        self.init_ui()
        self.restore_geometry()
        self.update_all_ui_text()
        self.load_prayer_times()
        self.start_tray_indicator()
        
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
        
    def init_ui(self):
        self.setWindowTitle('Salah Times')
        self.setMinimumSize(400, 600)
        self.resize(480, 720)
        self.setStyleSheet(self.get_modern_stylesheet())
        
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
                font-size: 16px;
                font-weight: 600;
            }
            
            .prayer_time {
                font-size: 18px;
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
        
        # Create grid layout
        grid = QGridLayout(container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)
        
        # Make rows and columns stretch equally
        for i in range(3):  # 3 rows
            grid.setRowStretch(i, 1)
        for i in range(2):  # 2 columns
            grid.setColumnStretch(i, 1)
        
        # Store prayer cards for updates
        self.prayer_cards = {}
        
        # Create placeholder cards (use Chorok instead of Sunrise)
        prayers = ['Fajr', 'Chorok', 'Dohr', 'Asr', 'Maghreb', 'Isha']
        icons = {'Fajr': '🌙', 'Chorok': '🌅', 'Dohr': '☀️', 
                'Asr': '🌇', 'Maghreb': '🌆', 'Isha': '🌃'}
        
        for i, prayer in enumerate(prayers):
            card = self.create_prayer_card_widget(prayer, icons[prayer], "--:--")
            row = i // 2
            col = i % 2
            grid.addWidget(card, row, col)
            self.prayer_cards[prayer] = card
        
        return container
    
    def create_prayer_card_widget(self, prayer_name, icon, time, is_current=False):
        card = QWidget()
        card.setProperty("class", "prayer_card_current" if is_current else "prayer_card")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(5)
        
        # Icon and name row
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setProperty("class", "prayer_icon")
        top_layout.addWidget(icon_label)
        
        name_label = QLabel(self.tr_prayer(prayer_name))
        name_label.setProperty("class", "prayer_name")
        name_label.setWordWrap(True)
        top_layout.addWidget(name_label)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Time
        time_label = QLabel(time)
        time_label.setProperty("class", "prayer_time")
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setWordWrap(True)
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
        
        # Refresh button
        self.refresh_btn = QPushButton()
        self.refresh_btn.setProperty("class", "modern_button")
        self.refresh_btn.clicked.connect(self.load_prayer_times)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.refresh_btn)
        
        return controls
        
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
        for prayer in ['Fajr', 'Chorok', 'Dohr', 'Asr', 'Maghreb', 'Isha']:
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
        city_id = CITIES.get(self.current_city, {'id': 101})['id']
        self.worker = PrayerTimeWorker(city_id, self.current_city)
        self.worker.data_received.connect(self.display_prayer_times)
        self.worker.offline_data_loaded.connect(self.display_offline_prayer_times)
        self.worker.error_occurred.connect(self.show_error)
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
        
        # Calculate Chorok locally using solar formula
        today = datetime.now()
        calculated_chorok = OfflineSunriseCalculator.calculate_sunrise(self.current_city, today)
        
        # Create display times: ignore scraped Sunrise, use calculated Chorok
        display_times = {}
        for prayer, time in prayer_times.items():
            if prayer != 'Sunrise':  # Skip scraped Sunrise completely
                display_times[prayer] = time
        
        # Add calculated Chorok
        if calculated_chorok:
            display_times['Chorok'] = calculated_chorok
        
        # Update prayer cards with new times and styling
        for prayer, time in display_times.items():
            if prayer in self.prayer_cards and prayer != 'Date':
                card = self.prayer_cards[prayer]
                is_current = (prayer == current_prayer or (prayer == 'Chorok' and current_prayer == 'Sunrise'))
                
                # Update card styling
                card.setProperty("class", "prayer_card_current" if is_current else "prayer_card")
                card.setStyleSheet(self.get_modern_stylesheet())  # Refresh styles
                
                # Update both prayer name and time text
                for child in card.findChildren(QLabel):
                    if child.property("class") == "prayer_name":
                        child.setText(self.tr_prayer(prayer))  # Update translated name
                    elif child.property("class") == "prayer_time":
                        child.setText(time)
                        child.setStyleSheet("")  # Clear any error styling
        
        # Update refresh button
        if hasattr(self, 'refresh_btn'):
            self.refresh_btn.setText(self.tr('refresh'))
        
        self.update_next_prayer()
        self.update_countdown()
    
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
    
    def get_iqama_times(self):
        """Get current Iqama times from inputs"""
        if hasattr(self, 'iqama_inputs'):
            return {prayer: input_widget.value() for prayer, input_widget in self.iqama_inputs.items()}
        return self.iqama_times
    
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
        # Show error in prayer cards
        for prayer in ['Fajr', 'Chorok', 'Dohr', 'Asr', 'Maghreb', 'Isha']:
            if hasattr(self, 'prayer_cards') and prayer in self.prayer_cards:
                card = self.prayer_cards[prayer]
                for child in card.findChildren(QLabel):
                    if child.property("class") == "prayer_time":
                        child.setText("Error")
                        child.setStyleSheet("color: #ff4444;")
    
    def start_tray_indicator(self):
        """Start the tray indicator if not already running"""
        try:
            # Check if tray indicator is already running
            result = subprocess.run(['pgrep', '-f', 'salah_tray_indicator.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return  # Already running
            
            # Start tray indicator
            script_dir = os.path.dirname(os.path.abspath(__file__))
            tray_script = os.path.join(script_dir, 'salah_tray_indicator.py')
            
            if os.path.exists(tray_script):
                self.tray_process = subprocess.Popen([sys.executable, tray_script])
        except Exception as e:
            print(f"Could not start tray indicator: {e}")
    
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
    
    def closeEvent(self, event):
        """Handle window close - save geometry and don't close tray indicator"""
        self.save_geometry()
        event.accept()  # Allow window to close, tray stays running

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Salah Times")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Islamic Apps")
    
    # Don't quit when last window is closed (tray should keep running)
    app.setQuitOnLastWindowClosed(False)
    
    window = ModernSalahApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()