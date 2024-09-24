import requests
from lxml import html
import sqlite3
import time
from functools import lru_cache

from lib import get_saved_institutes

# URL страницы с расписанием
url = "https://mai.ru/education/studies/schedule/groups.php"

# Кешируем результат парсинга
@lru_cache(maxsize=1)
def fetch_html():
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Ошибка загрузки страницы: {response.status_code}")
    return response.content

def parse_institutes(update_progress=None):
    # Получаем сохраненные институты из БД
    saved_institutes = get_saved_institutes()
    saved_institute_ids = {institute[0] for institute in saved_institutes}  # Множество ID сохраненных институтов
    
    # Если все институты уже сохранены, возвращаем их
    if saved_institute_ids:
        if update_progress:
            total_institutes = len(saved_institute_ids)
            for idx in range(total_institutes):
                update_progress(idx + 1, total_institutes)
        return saved_institutes
    
    # Если не все институты сохранены — парсим сайт
    content = fetch_html()  # Получаем HTML
    tree = html.fromstring(content)
    
    institutes = tree.xpath('/html/body/main/div/div/div[1]/article/form/div/div[1]/select/option')
    institute_data = []
    
    total_institutes = len(institutes)
    progress = len(saved_institute_ids)  # Прогресс начинается с количества сохраненных институтов
    
    for idx, institute in enumerate(institutes):
        institute_id = institute.get('value').strip().encode('latin1').decode()
        institute_name = institute.text.strip().encode('latin1').decode()
        
        # Если институт еще не сохранен, добавляем его в список для добавления в БД
        if institute_id and institute_id not in saved_institute_ids:
            institute_data.append((idx,institute_name))
            progress += 1  # Увеличиваем прогресс
        
        # Обновляем прогрессбар
        if update_progress:
            update_progress(progress, total_institutes)
        
        time.sleep(0.1)  # Для имитации долгого процесса
    
    return institute_data

# Функция для записи институтов в базу данных
def save_institutes_to_db(institute_data):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS institutes (
            id INTEGER,
            name TEXT PRIMARY KEY
        )
    ''')
    print(institute_data)
    cursor.execute('DELETE FROM institutes')
    cursor.executemany('INSERT INTO institutes (id, name) VALUES (?, ?)', institute_data)
    
    conn.commit()
    conn.close()