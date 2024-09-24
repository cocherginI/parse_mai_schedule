import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Подключение к базе данных SQLite
def create_db():
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    # Создаем таблицу, если она не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS schedule (
                        id INTEGER PRIMARY KEY,
                        group_name TEXT,
                        week INTEGER,
                        day TEXT,
                        time TEXT,
                        subject TEXT,
                        room TEXT
                    )''')
    
    # Пример данных для имитации
    cursor.execute('DELETE FROM schedule')  # Удаляем все предыдущие записи
    sample_data = [
        ('101', 1, 'Monday', '09:00', 'Math', 'Room 101'),
        ('101', 1, 'Monday', '11:00', 'Physics', 'Room 102'),
        ('101', 1, 'Tuesday', '10:00', 'Chemistry', 'Room 103'),
        ('102', 2, 'Wednesday', '09:00', 'Math', 'Room 104'),
        ('102', 2, 'Wednesday', '11:00', 'Biology', 'Room 105'),
    ]
    
    cursor.executemany('INSERT INTO schedule (group_name, week, day, time, subject, room) VALUES (?, ?, ?, ?, ?, ?)', sample_data)
    
    conn.commit()
    conn.close()

# Функция для поиска расписания по группе и неделе
def get_schedule(group, week):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT day, time, subject, room FROM schedule WHERE group_name=? AND week=?', (group, week))
    rows = cursor.fetchall()
    
    conn.close()
    return rows

# Обработка кнопки поиска
def search_schedule():
    group = group_entry.get()
    week = week_entry.get()
    
    if not group or not week:
        messagebox.showwarning("Ошибка", "Введите группу и неделю!")
        return
    
    try:
        week = int(week)
    except ValueError:
        messagebox.showwarning("Ошибка", "Неделя должна быть числом!")
        return
    
    schedule = get_schedule(group, week)
    
    # Очистка старого расписания
    for row in tree.get_children():
        tree.delete(row)
    
    # Добавление нового расписания
    if schedule:
        for row in schedule:
            tree.insert("", "end", values=row)
    else:
        messagebox.showinfo("Результат", "Расписание не найдено для данной группы и недели.")

# Создание основного окна приложения
root = tk.Tk()
root.title("Расписание")

# Поля для ввода группы и недели
tk.Label(root, text="Группа").grid(row=0, column=0, padx=10, pady=10)
group_entry = tk.Entry(root)
group_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Неделя").grid(row=1, column=0, padx=10, pady=10)
week_entry = tk.Entry(root)
week_entry.grid(row=1, column=1, padx=10, pady=10)

# Кнопка для поиска расписания
search_button = tk.Button(root, text="Показать расписание", command=search_schedule)
search_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Таблица для отображения расписания
columns = ("День", "Время", "Предмет", "Аудитория")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Запуск приложения и инициализация базы данных
create_db()
root.mainloop()
