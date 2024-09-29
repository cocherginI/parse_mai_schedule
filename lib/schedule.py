import sqlite3

from lib.db import get_saved_schedule
from lib.parsers import parse_schedule

# Получение расписания для группы
def fetch_schedule(group_name, week):
    schedule = get_saved_schedule(week, group_name)
    if not schedule:
        schedule = parse_schedule(group_name, week)
    return schedule
