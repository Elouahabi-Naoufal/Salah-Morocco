#!/usr/bin/env python3
"""
Android version using Kivy
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import threading
import json
import os

# Cities and translations
CITIES = {
    'Tangier': {'id': 101, 'en': 'Tangier', 'ar': 'طنجة', 'fr': 'Tanger'},
    'Casablanca': {'id': 71, 'en': 'Casablanca', 'ar': 'الدار البيضاء', 'fr': 'Casablanca'},
    'Rabat': {'id': 95, 'en': 'Rabat', 'ar': 'الرباط', 'fr': 'Rabat'},
    'Marrakech': {'id': 88, 'en': 'Marrakech', 'ar': 'مراكش', 'fr': 'Marrakech'},
    'Fes': {'id': 78, 'en': 'Fes', 'ar': 'فاس', 'fr': 'Fes'},
    'Agadir': {'id': 66, 'en': 'Agadir', 'ar': 'أكادير', 'fr': 'Agadir'},
    'Meknes': {'id': 89, 'en': 'Meknes', 'ar': 'مكناس', 'fr': 'Meknes'},
    'Oujda': {'id': 93, 'en': 'Oujda', 'ar': 'وجدة', 'fr': 'Oujda'},
}

TRANSLATIONS = {
    'en': {
        'app_title': 'Salah Times',
        'next_prayer': 'NEXT PRAYER',
        'loading': 'Loading prayer times...',
        'refresh': 'Refresh',
        'morocco': 'Morocco',
        'prayers': {
            'Fajr': 'Fajr', 'Sunrise': 'Sunrise', 'Dohr': 'Dhuhr',
            'Asr': 'Asr', 'Maghreb': 'Maghrib', 'Isha': 'Isha'
        }
    },
    'ar': {
        'app_title': 'مواقيت الصلاة',
        'next_prayer': 'الصلاة القادمة',
        'loading': 'جاري تحميل مواقيت الصلاة...',
        'refresh': 'تحديث',
        'morocco': 'المغرب',
        'prayers': {
            'Fajr': 'الفجر', 'Sunrise': 'الشروق', 'Dohr': 'الظهر',
            'Asr': 'العصر', 'Maghreb': 'المغرب', 'Isha': 'العشاء'
        }
    },
    'fr': {
        'app_title': 'Horaires de Priere',
        'next_prayer': 'PROCHAINE PRIERE',
        'loading': 'Chargement des horaires de priere...',
        'refresh': 'Actualiser',
        'morocco': 'Maroc',
        'prayers': {
            'Fajr': 'Fajr', 'Sunrise': 'Lever du soleil', 'Dohr': 'Dhuhr',
            'Asr': 'Asr', 'Maghreb': 'Maghrib', 'Isha': 'Isha'
        }
    }
}

class SalahTimesApp(App):
    def __init__(self):
        super().__init__()
        self.current_language = 'en'
        self.current_city = 'Tangier'
        self.prayer_times = {}
        self.is_offline = False
        self.days_remaining = 0
        self.storage_file = os.path.join(os.path.expanduser('~'), 'Documents', f'salah_times_{self.current_city.lower()}.json')
        
    def build(self):
        self.title = 'Salah Times'
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Header
        header_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=dp(5))
        
        self.title_label = Label(
            text='🕌 Salah Times',
            font_size=dp(24),
            color=(0.18, 0.35, 0.15, 1),
            bold=True
        )
        header_layout.add_widget(self.title_label)
        
        self.location_label = Label(
            text=f'{self.current_city}, Morocco',
            font_size=dp(16),
            color=(0.5, 0.5, 0.5, 1)
        )
        header_layout.add_widget(self.location_label)
        
        self.offline_indicator = Label(
            text='',
            font_size=dp(12),
            color=(1, 0.4, 0.2, 1),
            size_hint_y=None,
            height=dp(20)
        )
        header_layout.add_widget(self.offline_indicator)
        
        main_layout.add_widget(header_layout)
        
        # Controls
        controls_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # Language selector
        self.language_spinner = Spinner(
            text='English',
            values=['English', 'العربية', 'Français'],
            size_hint_x=0.5
        )
        self.language_spinner.bind(text=self.on_language_change)
        controls_layout.add_widget(self.language_spinner)
        
        # City selector
        city_names = list(CITIES.keys())
        self.city_spinner = Spinner(
            text=self.current_city,
            values=city_names,
            size_hint_x=0.5
        )
        self.city_spinner.bind(text=self.on_city_change)
        controls_layout.add_widget(self.city_spinner)
        
        main_layout.add_widget(controls_layout)
        
        # Prayer times scroll area
        scroll = ScrollView()
        self.prayer_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.prayer_layout.bind(minimum_height=self.prayer_layout.setter('height'))
        scroll.add_widget(self.prayer_layout)
        main_layout.add_widget(scroll)
        
        # Refresh button
        refresh_btn = Button(
            text='Refresh',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.18, 0.35, 0.15, 1)
        )
        refresh_btn.bind(on_press=self.refresh_prayer_times)
        main_layout.add_widget(refresh_btn)
        
        # Load initial data
        Clock.schedule_once(lambda dt: self.refresh_prayer_times(), 1)
        
        return main_layout
    
    def on_language_change(self, spinner, text):
        lang_map = {'English': 'en', 'العربية': 'ar', 'Français': 'fr'}
        self.current_language = lang_map.get(text, 'en')
        self.update_ui_text()
        
    def on_city_change(self, spinner, text):
        self.current_city = text
        self.storage_file = os.path.join(os.path.expanduser('~'), 'Documents', f'salah_times_{self.current_city.lower()}.json')
        self.location_label.text = f'{self.current_city}, {self.tr("morocco")}'
        self.refresh_prayer_times()
        
    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)
        
    def tr_prayer(self, prayer_key):
        return TRANSLATIONS[self.current_language]['prayers'].get(prayer_key, prayer_key)
        
    def update_ui_text(self):
        self.title_label.text = f'🕌 {self.tr("app_title")}'
        self.location_label.text = f'{self.current_city}, {self.tr("morocco")}'
        
    def refresh_prayer_times(self, *args):
        # Clear current display
        self.prayer_layout.clear_widgets()
        
        # Show loading
        loading_label = Label(
            text=self.tr('loading'), 
            font_size=dp(16),
            size_hint_y=None,
            height=dp(50)
        )
        self.prayer_layout.add_widget(loading_label)
        
        # Fetch prayer times in background thread
        threading.Thread(target=self.fetch_prayer_times, daemon=True).start()
        
    def fetch_prayer_times(self):
        try:
            city_id = CITIES.get(self.current_city, {'id': 101})['id']
            url = f'https://www.yabiladi.com/prieres/details/{city_id}/city.html'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            prayer_table = soup.find('table')
            
            if prayer_table:
                headers = [header.text.strip() for header in prayer_table.find_all('th')]
                rows = prayer_table.find_all('tr')[1:]
                
                today = datetime.now().strftime('%d/%m')
                
                for row in rows:
                    columns = row.find_all('td')
                    if columns and columns[0].text.strip() == today:
                        prayer_times = {}
                        for header, col in zip(headers, columns):
                            prayer_times[header] = col.text.strip()
                        
                        Clock.schedule_once(lambda dt: self.display_prayer_times(prayer_times))
                        return
            
            Clock.schedule_once(lambda dt: self.show_error("No prayer times found"))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(str(e)))
    
    def display_prayer_times(self, prayer_times):
        self.prayer_layout.clear_widgets()
        
        for prayer, time in prayer_times.items():
            if prayer != 'Date':
                prayer_layout = BoxLayout(
                    orientation='horizontal', 
                    size_hint_y=None, 
                    height=dp(60),
                    padding=[dp(15), dp(10)]
                )
                
                # Prayer icon
                icon_label = Label(
                    text='🕐',
                    font_size=dp(20),
                    size_hint_x=None,
                    width=dp(40)
                )
                prayer_layout.add_widget(icon_label)
                
                # Prayer name
                prayer_name = Label(
                    text=self.tr_prayer(prayer),
                    font_size=dp(18),
                    halign='left',
                    bold=True,
                    color=(0.18, 0.35, 0.15, 1)
                )
                prayer_name.bind(size=prayer_name.setter('text_size'))
                prayer_layout.add_widget(prayer_name)
                
                # Prayer time
                prayer_time = Label(
                    text=time,
                    font_size=dp(18),
                    halign='right',
                    bold=True,
                    size_hint_x=None,
                    width=dp(80)
                )
                prayer_time.bind(size=prayer_time.setter('text_size'))
                prayer_layout.add_widget(prayer_time)
                
                self.prayer_layout.add_widget(prayer_layout)
    
    def show_error(self, message):
        self.prayer_layout.clear_widgets()
        error_label = Label(
            text=f'Error: {message}',
            font_size=dp(16),
            color=(1, 0, 0, 1),
            size_hint_y=None,
            height=dp(100)
        )
        self.prayer_layout.add_widget(error_label)

if __name__ == '__main__':
    SalahTimesApp().run()