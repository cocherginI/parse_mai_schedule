import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from lib.parsers import parse_groups_for_institute, parse_institutes
from lib.db import create_db, get_saved_institutes, get_groups_for_institute
from lib.schedule import fetch_schedule

# Инициализация базы данных
create_db()

# Функция для показа расписания
def show_schedule():
    group = group_entry.get()
    week = week_entry.get()

    if not group:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите группу.")
        return
    
    try:
        schedule_data = fetch_schedule(group, week)
        for row in schedule_data:
            schedule_tree.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить расписание: {str(e)}")

# Функция для обновления прогресс-бара в главном потоке
def update_progress_in_main(progress, total, bar, label, text):
    root.after(0, update_progress, progress, total, bar, label, text)

# Функция для обновления прогресс-бара
def update_progress(progress, total, bar, label, text):
    bar["value"] = progress
    bar["maximum"] = total
    label.config(text=f"{text}: {progress}/{total}")

# Инициализация интерфейса
root = tk.Tk()
root.title("Парсинг Институтов и Групп, Просмотр Расписания")

# Виджеты для института
tk.Label(root, text="Институт").grid(row=0, column=0, padx=10, pady=10)
institute_combobox = ttk.Combobox(root)
institute_combobox.grid(row=0, column=1, padx=10, pady=10)

# Виджеты для группы
tk.Label(root, text="Группа").grid(row=1, column=0, padx=10, pady=10)
group_entry = tk.Entry(root)
group_entry.grid(row=1, column=1, padx=10, pady=10)

# Поле для недели
tk.Label(root, text="Неделя").grid(row=2, column=0, padx=10, pady=10)
week_entry = tk.Entry(root)
week_entry.grid(row=2, column=1, padx=10, pady=10)

# Кнопка для показа расписания
schedule_button = tk.Button(root, text="Показать расписание", command=show_schedule)
schedule_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Таблица для отображения расписания
schedule_tree = ttk.Treeview(root, columns=("Время", "Предмет", "Преподаватель", "Аудитория"), show="headings")
schedule_tree.heading("Время", text="Время")
schedule_tree.heading("Предмет", text="Предмет")
schedule_tree.heading("Преподаватель", text="Преподаватель")
schedule_tree.heading("Аудитория", text="Аудитория")
schedule_tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Прогрессбар и текстовые метки
progress_label = tk.Label(root, text="Загрузка институтов...")
progress_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Функция инициализации интерфейса
def initialize_interface():
    institutes = get_saved_institutes()
    
    if institutes:
        institute_combobox['values'] = [inst[1] for inst in institutes]
        if institutes:
            institute_combobox.current(0)
        # Обновляем прогресс для уже сохраненных институтов
        update_progress_in_main(len(institutes), len(institutes), progress_bar, progress_label, "Загрузка институтов")
        
        # Параллельно продолжаем парсинг групп и расписания
        # for institute in institutes[1:]:
        #     institute = (None, institute[1].replace(' ', '+'))
        #     thread = Thread(target=parse_groups_and_schedule, args=(institute))
        #     thread.start()
    else:
        messagebox.showinfo("Парсинг", "Институты не найдены. Запускаем парсинг...")

        # Запускаем парсинг в отдельном потоке
        thread = Thread(target=parse_institutes_and_groups)
        thread.start()

# Основная функция парсинга институтов, групп и расписания
def parse_institutes_and_groups():
    try:
        institutes = get_saved_institutes()
        if not institutes:
            # Парсинг институтов
            institutes = parse_institutes(lambda p, t: update_progress_in_main(p, t, progress_bar, progress_label, "Загрузка институтов"))

        # Параллельно парсим группы и расписание
        for institute in institutes:
            groups = get_groups_for_institute(institute)
            if not groups:
                parse_groups_and_schedule(None, institute)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при парсинге: {e}")

# Парсинг групп и расписания
def parse_groups_and_schedule(self, institute):
    try:
        # Парсинг групп
        # parse_groups_for_institute(institute)
        
        # # Парсинг расписания
        # parse_schedule_for_all_groups(lambda p, t: update_progress_in_main(p, t, progress_bar, progress_label, "Загрузка расписания"))
        groups = get_groups_for_institute(institute)
        if not groups:        
            messagebox.showinfo("Парсинг", "Все данные успешно загружены.")


        messagebox.showinfo("Парсинг", "Все данные успешно загружены.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при парсинге: {e}")

# Инициализация интерфейса
initialize_interface()

root.mainloop()
