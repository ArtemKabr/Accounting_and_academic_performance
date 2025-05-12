import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TEACHER_PASSWORD = os.getenv("TEACHER_PASSWORD", "4321")
PARENT_PASSWORD = os.getenv("PARENT_PASSWORD", "1234")


