import json
from pathlib import Path
from datetime import datetime

# Пути к файлам
DATA_DIR = Path("src/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = DATA_DIR / "users.json"
SCHEDULE_FILE = DATA_DIR / "schedule.json"
BEHAVIOR_FILE = DATA_DIR / "behavior.json"

# ----------- USERS ----------------
def save_user_data(user_id: str, data: dict):
    users = {}
    if DB_FILE.exists():
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except json.JSONDecodeError:
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

# ----------- SCHEDULE -------------
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

# ----------- BEHAVIOR -------------
def load_behavior_data() -> list:
    if not BEHAVIOR_FILE.exists():
        return []
    try:
        with open(BEHAVIOR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def append_behavior_entry(entry: dict):
    entry["дата"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data = load_behavior_data()  # ты уже внутри этого модуля!
    data.append(entry)
    with open(BEHAVIOR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


