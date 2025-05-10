# Загрузка/сохранение JSON.

import json
import os
from config import USERS_DB_PATH, SCHEDULE_PATH

def load_users_db():
    if os.path.exists(USERS_DB_PATH):
        with open(USERS_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            for user_id, user_data in data.items():
                if "role" not in user_data:
                    user_data["role"] = "parent"
                if "role_name" not in user_data:
                    user_data["role_name"] = "Родитель" if user_data["role"] == "parent" else "Учитель"
                if "access" not in user_data:
                    user_data["access"] = True
            return data
    return {}

def load_schedule():
    try:
        if os.path.exists(SCHEDULE_PATH):
            with open(SCHEDULE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Ошибка загрузки расписания: {e}")
        return {}

def save_users_db(data):
    try:
        with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения пользователей: {e}")
        return False
