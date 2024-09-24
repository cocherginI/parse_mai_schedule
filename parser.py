import requests
from lxml import html
import sqlite3
import time
from functools import lru_cache

# URL страницы с расписанием
url = "https://mai.ru/education/studies/schedule/groups.php"

# Кешируем результат парсинга
@lru_cache(maxsize=1)
def fetch_html():
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Ошибка загрузки страницы: {response.status_code}")
    return response.content

# Функция для парсинга списка институтов
def parse_institutes(update_progress=None):
    content = fetch_html()  # Получаем HTML (с кешированием)
    tree = html.fromstring(content)
    
    institutes = tree.xpath('/html/body/main/div/div/div[1]/article/form/div/div[1]/select/option')
    institute_data = []
    
    total_institutes = len(institutes)
    for idx, institute in enumerate(institutes):
        institute_id = institute.get('value')
        institute_name = institute.text.strip()
        if institute_id:  # Пропускаем пустые элементы
            institute_data.append((institute_id, institute_name))
        
        # Обновляем прогресс
        if update_progress:
            update_progress(idx + 1, total_institutes)
        time.sleep(0.1)  # Для имитации долгого процесса
    
    return institute_data

# Функция для записи институтов в базу данных
def save_institutes_to_db(institute_data):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS institutes (
            id TEXT PRIMARY KEY,
            name TEXT
        )
    ''')
    
    cursor.execute('DELETE FROM institutes')
    cursor.executemany('INSERT INTO institutes (id, name) VALUES (?, ?)', institute_data)
    
    conn.commit()
    conn.close()
