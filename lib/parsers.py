import requests
from lxml import html
import time
from lib.db import save_institutes_to_db, save_groups_to_db, save_schedule_to_db

# Функция парсинга институтов
def parse_institutes(update_progress):
    url = "https://mai.ru/education/studies/schedule/groups.php"
    response = requests.get(url)
    tree = html.fromstring(response.content)
    
    institutes = tree.xpath('/html/body/main/div/div/div[1]/article/form/div/div[1]/select/option')
    institute_data = [(institute.text.encode('l1').decode().strip(),) for institute in institutes if institute.text.strip()]
    
    save_institutes_to_db(institute_data)
    
    total = len(institute_data)
    for idx in range(total):
        time.sleep(0.1)  # Имитируем длительную операцию
        update_progress(idx + 1, total)
    
    return institute_data

# Функция парсинга групп для одного института
def parse_groups_for_institute(institute):
    group_data = []
    
    url = f"https://mai.ru/education/studies/schedule/groups.php?department={institute}&course=all"
    response = requests.get(url)
    
    tree = html.fromstring(response.content)
    
    groups = tree.xpath('//a[contains(@href, "index.php?group=")]')
    group_data.extend([(institute, group.text.encode('l1').decode().strip()) for group in groups])
    save_groups_to_db(group_data)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # автоматическая установка chromedriver
from lib.db import save_schedule_to_db

# Настройки Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

from chromedriver_py import binary_path # this will get you the path variable

svc = webdriver.ChromeService(executable_path=binary_path)
driver = webdriver.Chrome(service=svc, options=chrome_options)

# Функция парсинга расписания для одной группы на конкретную неделю
def parse_schedule(group_name, week):
    schedule_data = []
    url = f"https://mai.ru/education/studies/schedule/index.php?group={group_name}&week={week}"

    try:
        # Переход на страницу
        driver.get(url)

        # Ожидание загрузки элементов
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//li[contains(@class, "step-item")]'))
        )

        # Находим элементы для каждого дня
        day_elements = driver.find_elements(By.XPATH, '//li[contains(@class, "step-item")]')

        for day_element in day_elements:
            # День недели
            day = day_element.find_element(By.XPATH, './/span[contains(@class, "step-title")]').text.strip()

            # Находим все занятия для этого дня
            lesson_elements = day_element.find_elements(By.XPATH, './/div[contains(@class, "mb-4")]')
            
            for lesson in lesson_elements:
                # Время занятия
                time = lesson.find_element(By.XPATH, './/li[contains(@class, "list-inline-item")]').text.strip()

                # Название предмета
                subject = lesson.find_element(By.XPATH, './/p[contains(@class, "fw-semi-bold text-dark")]').text.strip()

                # Преподаватель
                teacher_elements = lesson.find_elements(By.XPATH, './/li[contains(@class, "list-inline-item")]/a')
                teacher = teacher_elements[0].text.strip() if teacher_elements else "Преподаватель не указан"

                # Аудитория
                room_elements = lesson.find_elements(By.XPATH, './/li[contains(@class, "list-inline-item")]/i[contains(@class, "fa-map-marker-alt")]/following-sibling::text()')
                room = room_elements[0].strip() if room_elements else "Аудитория не указана"

                # Добавляем данные в список для записи в БД
                schedule_data.append((group_name, week, day, time, subject, teacher, room))

    except Exception as e:
        print(f"Ошибка парсинга страницы для группы {group_name}, неделя {week}: {e}")

    finally:
        # Закрытие браузера
        driver.quit()

    # Сохраняем данные в базу данных
    save_schedule_to_db(schedule_data)
    return schedule_data
