import sqlite3

# Создание таблиц базы данных
def create_db():
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS institutes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institute_id INTEGER,
            name TEXT UNIQUE,
            FOREIGN KEY (institute_id) REFERENCES institutes(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT,
            week INTEGER,
            day TEXT,
            time TEXT,
            subject TEXT,
            teacher TEXT,
            room TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Сохранение институтов в БД
def save_institutes_to_db(institutes):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.executemany('INSERT OR IGNORE INTO institutes (name) VALUES (?)', institutes)
    conn.commit()
    conn.close()

# Получение сохраненных институтов
def get_saved_institutes():
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name FROM institutes')
    institutes = cursor.fetchall()
    conn.close()
    
    return institutes

# Получение сохраненных институтов
def get_saved_schedule(week, group_name):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT group_name, week, day, time, subject, teacher, room 
        FROM schedule
        WHERE week = ? AND group_name = ?
    ''', (week, group_name))
    schedule = cursor.fetchall()
    conn.close()
    
    return schedule

# Сохранение групп в БД
def save_groups_to_db(groups):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.executemany('INSERT OR IGNORE INTO groups (institute_id, name) VALUES (?, ?)', groups)
    conn.commit()
    conn.close()

# Получение групп для института
def get_groups_for_institute(institute_name):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT groups.name
        FROM groups
        JOIN institutes ON institutes.id = groups.institute_id
        WHERE institutes.name = ?
    ''', (institute_name,))
    
    groups = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return groups
    
def save_schedule_to_db(schedules):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO schedule (group_name, week, day, time, subject, teacher, room) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', schedules)
    
    conn.commit()
    conn.close()