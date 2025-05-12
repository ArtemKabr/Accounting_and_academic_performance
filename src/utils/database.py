import json
from pathlib import Path

# Новые пути
DB_FILE = Path("data/users.json")
SCHEDULE_FILE = Path("data/schedule.json")

# Гарантируем, что папка существует
DB_FILE.parent.mkdir(parents=True, exist_ok=True)

def save_user_data(user_id: str, data: dict):
    if DB_FILE.exists():
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except json.JSONDecodeError:
            users = {}
    else:
        users = {}

    users[user_id] = data

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def load_user_data(user_id: str) -> dict | None:
    if not DB_FILE.exists():
        return None
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
        return users.get(user_id)
    except json.JSONDecodeError:
        return None

def load_schedule() -> dict:
    if not SCHEDULE_FILE.exists():
        return {}
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_schedule(data: dict):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
