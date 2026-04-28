import requests, sqlite3, time
from bs4 import BeautifulSoup

# Map each city name to its (url_id, slug)
cities = {
    'Agadir':                (66,  'agadir'),
    'Al Hoceima':            (79,  'al-hoceima'),
    'Assila':                (67,  'assila'),
    'Beni Mellal':           (68,  'beni-mellal'),
    'Berkane':               (69,  'berkane'),
    'Boulemane':             (70,  'boulemane'),
    'Casablanca':            (71,  'casablanca'),
    'Chefchaouen':           (72,  'chefchaouen'),
    'Dakhla':                (73,  'dakhla'),
    'El Jadida':             (74,  'el-jadida'),
    'Errachidia':            (75,  'errachidia'),
    'Essaouira':             (76,  'essaouira'),
    'Fes':                   (78,  'fes'),
    'Ifrane':                (80,  'ifrane'),
    'Kalaat Sraghna':        (94,  'kalaat-sraghna'),
    'Kenitra':               (81,  'kenitra'),
    'Khenifra':              (82,  'khenifra'),
    'Khouribga':             (83,  'khouribga'),
    'Ksar Lekbir':           (84,  'ksar-lekbir'),
    'Laayoune':              (85,  'laayoune'),
    'Lagouira':              (86,  'lagouira'),
    'Larache':               (87,  'larache'),
    'Marrakech':             (88,  'marrakech'),
    'Meknes':                (89,  'meknes'),
    'Mohammedia':            (90,  'mohammedia'),
    'Moulay Idriss Zerhoun': (108, 'moulay-idriss-zerhoun'),
    'Nador':                 (91,  'nador'),
    'Ouazzane':              (92,  'ouazzane'),
    'Oujda':                 (93,  'oujda'),
    'Rabat':                 (95,  'rabat'),
    'Safi':                  (96,  'safi'),
    'Sefrou':                (97,  'sefrou'),
    'Settat':                (98,  'settat'),
    'Sidi Kacem':            (99,  'sidi-kacem'),
    'Smara':                 (77,  'smara'),
    'Tan-Tan':               (102, 'tan-tan'),
    'Tanger':                (101, 'tanger'),
    'Taounate':              (104, 'taounate'),
    'Taroudant':             (103, 'taroudant'),
    'Taza':                  (105, 'taza'),
    'Tetouan':               (100, 'tetouan'),
    'Tiznit':                (106, 'tiznit'),
    'Zagora':                (107, 'zagora'),
}

BASE_URL = 'https://www.yabiladi.com/prieres/details/{}/{}.html'
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

conn = sqlite3.connect('salah.db')
cursor = conn.cursor()

for city_name, (city_id, slug) in cities.items():
    table = slug.replace('-', '_')
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            date TEXT, fajr TEXT, dohr TEXT,
            asr TEXT, maghreb TEXT, isha TEXT
        )
    """)
    url = BASE_URL.format(city_id, slug)
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    table_html = soup.find('table', class_='prayer')
    if not table_html:
        print(f'SKIP {city_name} - table not found')
        continue
    rows = []
    for tr in table_html.find_all('tr')[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all('td')]
        if cells:
            rows.append(cells)
    cursor.executemany(
        f'INSERT INTO {table} (date, fajr, dohr, asr, maghreb, isha) VALUES (?, ?, ?, ?, ?, ?)',
        rows
    )
    conn.commit()
    print(f'OK  {city_name:30s} -> {len(rows)} rows')
    time.sleep(1)

conn.close()
print('Done!')
