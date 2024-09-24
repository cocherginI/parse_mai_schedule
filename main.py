import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import parser  # Импортируем наш модуль с парсингом

# Очередь для передачи сообщений между потоками
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

# Создание основного окна
root = tk.Tk()
root.title("Расписание")

# Поля для ввода группы и недели (предыдущее из вашего приложения)
tk.Label(root, text="Группа").grid(row=0, column=0, padx=10, pady=10)
group_entry = tk.Entry(root)
group_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Неделя").grid(row=1, column=0, padx=10, pady=10)
week_entry = tk.Entry(root)
week_entry.grid(row=1, column=1, padx=10, pady=10)

# Кнопка для поиска расписания (предыдущее из вашего приложения)
search_button = tk.Button(root, text="Показать расписание")
search_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Прогресс бар для парсинга
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var)
progress_bar.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

progress_label = tk.Label(root, text="Прогресс: 0/0")
progress_label.grid(row=4, column=0, columnspan=2)

# Кнопка для запуска парсинга
parse_button = tk.Button(root, text="Парсинг институтов", command=start_parsing_thread)
parse_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Обновление прогресс бара
update_progress_bar()

# Запуск основного цикла
root.mainloop()
