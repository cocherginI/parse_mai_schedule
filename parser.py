import requests
from lxml import html
import sqlite3

# URL страницы с расписанием
url = "https://mai.ru/education/studies/schedule/groups.php"

# Функция для парсинга списка институтов
def parse_institutes():
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Ошибка загрузки страницы: {response.status_code}")
    
    # Парсим содержимое страницы
    tree = html.fromstring(response.content)
    
    # Используем XPath для поиска списка институтов
    institutes = tree.xpath('/html/body/main/div/div/div[1]/article/form/div/div[1]/select/option')
    
    # Извлекаем данные (id и название института)
    institute_data = []
    for institute in institutes[1:]: # Пропускаем первое
        institute_id = institute.get('value')
        institute_name = institute.text.strip()
        if institute_id:  # Пропускаем пустые элементы
            institute_data.append((institute_id, institute_name))
    
    return institute_data

# Функция для создания таблицы "institutes" и записи данных в базу
def save_institutes_to_db(institute_data):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    # Создаем таблицу, если она не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS institutes (
            id TEXT PRIMARY KEY,
            name TEXT
        )
    ''')
    
    # Очищаем таблицу перед записью новых данных
    cursor.execute('DELETE FROM institutes')
    
    # Добавляем данные в таблицу
    cursor.executemany('INSERT INTO institutes (id, name) VALUES (?, ?)', institute_data)
    
    conn.commit()
    conn.close()

# Основная функция для парсинга и записи в базу
def run_parsing():
    try:
        institutes = parse_institutes()
        save_institutes_to_db(institutes)
        print(f"Успешно записано {len(institutes)} институтов в базу данных.")
    except Exception as e:
        print(f"Ошибка: {e}")

# Точка входа
if __name__ == "__main__":
    run_parsing()
