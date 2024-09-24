import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import threading
import queue
import parser  # Импортируем модуль с парсингом

# Очередь для передачи прогресса между потоками
progress_queue = queue.Queue()

# Функция для отображения прогресса
def update_progress_bar():
    try:
        while True:
            progress, total = progress_queue.get_nowait()
            progress_var.set(progress)
            progress_bar["maximum"] = total
            progress_label.config(text=f"Прогресс: {progress}/{total}")
            if progress >= total:
                break
    except queue.Empty:
        pass
    root.after(100, update_progress_bar)

# Функция для обновления прогресса из парсера
def update_progress(progress, total):
    progress_queue.put((progress, total))

# Функция для выполнения парсинга в отдельном потоке
def run_parsing():
    try:
        institutes = parser.parse_institutes(update_progress)
        parser.save_institutes_to_db(institutes)
        messagebox.showinfo("Парсинг", "Институты успешно добавлены в базу данных!")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# Функция для запуска парсинга в потоке
def start_parsing_thread():
    threading.Thread(target=run_parsing).start()

# Функция для получения расписания группы на неделю
def get_schedule(group, week):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()

    # Проверяем, есть ли группа
    cursor.execute('SELECT * FROM schedules WHERE group_id=? AND week=?', (group, week))
    schedule = cursor.fetchall()
    conn.close()

    return schedule

# Функция для отображения расписания
def show_schedule():
    group = group_entry.get()
    week = week_entry.get()

    if not group or not week:
        messagebox.showerror("Ошибка", "Пожалуйста, введите группу и неделю!")
        return

    schedule = get_schedule(group, week)
    
    if not schedule:
        messagebox.showinfo("Расписание", "Расписание не найдено.")
    else:
        # Очищаем текущее содержимое поля с расписанием
        schedule_text.delete(1.0, tk.END)
        schedule_text.insert(tk.END, f"Расписание для группы {group} на неделю {week}:\n\n")
        for day, subject, time in schedule:
            schedule_text.insert(tk.END, f"{day}: {subject} в {time}\n")

# Функция для создания таблиц базы данных
def create_database():
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()

    # Создание таблицы для расписаний
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT,
            week INTEGER,
            day TEXT,
            subject TEXT,
            time TEXT
        )
    ''')

    # Создание таблицы для институтов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS institutes (
            id TEXT PRIMARY KEY,
            name TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Создаем базу данных при запуске программы
create_database()

# Создание основного окна
root = tk.Tk()
root.title("Расписание")

# Поля для ввода группы и недели
tk.Label(root, text="Группа").grid(row=0, column=0, padx=10, pady=10)
group_entry = tk.Entry(root)
group_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Неделя").grid(row=1, column=0, padx=10, pady=10)
week_entry = tk.Entry(root)
week_entry.grid(row=1, column=1, padx=10, pady=10)

# Кнопка для показа расписания
search_button = tk.Button(root, text="Показать расписание", command=show_schedule)
search_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Текстовое поле для отображения расписания
schedule_text = tk.Text(root, height=10, width=50)
schedule_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Прогрессбар для парсинга
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var)
progress_bar.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

progress_label = tk.Label(root, text="Прогресс: 0/0")
progress_label.grid(row=5, column=0, columnspan=2)

# Кнопка для запуска парсинга
parse_button = tk.Button(root, text="Парсинг институтов", command=start_parsing_thread)
parse_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Обновление прогресс бара
update_progress_bar()

# Запуск основного цикла
root.mainloop()
