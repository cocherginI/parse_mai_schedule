import sqlite3
# Функция для получения сохраненных институтов из базы данных
def get_saved_institutes():
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM institutes')
    institutes = cursor.fetchall()
    conn.close()
    
    return institutes