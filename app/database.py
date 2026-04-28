import os
import sqlite3
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from .constants import CITIES, CITY_SLUGS, BASE_URL, SCRAPER_HEADERS

DB_PATH = os.path.join(os.path.expanduser('~'), '.salah_times', 'salah.db')
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.salah_times', 'config')


def get_today_prayer_times(city_name):
    return get_prayer_times_for_date(city_name, datetime.now().strftime('%d/%m'))


def get_prayer_times_for_date(city_name, date):
    try:
        slug = CITY_SLUGS.get(city_name)
        if not slug or not os.path.exists(DB_PATH):
            return None
        table = slug.replace('-', '_')
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f'SELECT date, fajr, dohr, asr, maghreb, isha FROM {table} WHERE date = ?', (date,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'Date': row[0], 'Fajr': row[1], 'Dohr': row[2],
                    'Asr': row[3], 'Maghreb': row[4], 'Isha': row[5]}
    except Exception as e:
        print(f"Error loading prayer times: {e}")
    return None


def get_all_prayer_times(city_name):
    try:
        slug = CITY_SLUGS.get(city_name)
        if not slug or not os.path.exists(DB_PATH):
            return {}
        table = slug.replace('-', '_')
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f'SELECT date, fajr, dohr, asr, maghreb, isha FROM {table}')
        rows = cursor.fetchall()
        conn.close()
        return {
            r[0]: {'Date': r[0], 'Fajr': r[1], 'Dohr': r[2],
                   'Asr': r[3], 'Maghreb': r[4], 'Isha': r[5]}
            for r in rows
        }
    except Exception as e:
        print(f"Error loading all prayer times for {city_name}: {e}")
    return {}


def update_all_cities():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for city_name, city_data in CITIES.items():
        slug = CITY_SLUGS.get(city_name)
        if not slug:
            continue
        city_id = city_data['id']
        table = slug.replace('-', '_')
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                date TEXT PRIMARY KEY, fajr TEXT, dohr TEXT,
                asr TEXT, maghreb TEXT, isha TEXT
            )
        """)
        try:
            url = BASE_URL.format(city_id, slug)
            resp = requests.get(url, headers=SCRAPER_HEADERS, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            prayer_table = soup.find('table', class_='prayer')
            if not prayer_table:
                print(f'SKIP {city_name} - table not found')
                continue
            rows = []
            for tr in prayer_table.find_all('tr')[1:]:
                cells = [td.get_text(strip=True) for td in tr.find_all('td')]
                if cells and len(cells) >= 6:
                    rows.append(cells[:6])
            cursor.execute(f'DELETE FROM {table}')
            cursor.executemany(
                f'INSERT INTO {table} (date, fajr, dohr, asr, maghreb, isha) VALUES (?, ?, ?, ?, ?, ?)',
                rows
            )
            conn.commit()
            print(f'OK  {city_name:30s} -> {len(rows)} rows')
        except Exception as e:
            print(f"Error updating {city_name}: {e}")
            continue
    conn.close()


def check_internet():
    try:
        response = requests.get('https://www.yabiladi.com', timeout=5)
        return response.status_code == 200
    except:
        return False


def get_db_info():
    result = {'cities': 0, 'first_date': 'N/A', 'last_date': 'N/A'}
    if not os.path.exists(DB_PATH):
        return result
    try:
        conn = sqlite3.connect(DB_PATH)
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


def get_day_counter_file():
    return os.path.join(CONFIG_DIR, 'day_counter.json')


def get_day_counter():
    try:
        with open(get_day_counter_file(), 'r') as f:
            data = json.load(f)
        last = datetime.fromisoformat(data['last_checked'])
        if datetime.now().date() > last.date():
            count = data.get('count', 0) + 1
            save_day_counter(count)
            return count
        return data.get('count', 0)
    except:
        save_day_counter(0)
        return 0


def save_day_counter(count):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(get_day_counter_file(), 'w') as f:
            json.dump({'count': count, 'last_checked': datetime.now().isoformat()}, f)
    except Exception as e:
        print(f"Could not save day counter: {e}")


def reset_day_counter():
    save_day_counter(0)


def db_exists():
    return os.path.exists(DB_PATH)
