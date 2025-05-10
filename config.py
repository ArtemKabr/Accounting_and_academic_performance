# Настройки: токены, пароли, пути к файлам.

import os

BOT_TOKEN = "7204660500:AAF9mD9F6q-_QkFaL9U_d6dW7mbZ2rRD-WY"
ADMIN_PASSWORD = "12345"
TEACHER_PASSWORD = "123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_DB_PATH = os.path.join(BASE_DIR, "database", "users_db.json")
SCHEDULE_PATH = os.path.join(BASE_DIR, "database", "schedule.json")
