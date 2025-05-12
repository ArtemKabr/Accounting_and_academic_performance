import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from src.utils import database

class TestSystemLogic(unittest.TestCase):

    def test_schedule_save_and_load(self):
        schedule = {
            "Понедельник": ["Математика", "Русский язык"],
            "Вторник": ["Физика"]
        }
        database.save_schedule(schedule)
        loaded = database.load_schedule()
        self.assertEqual(loaded["Понедельник"], ["Математика", "Русский язык"])
        self.assertEqual(loaded["Вторник"], ["Физика"])

    def test_empty_schedule(self):
        database.save_schedule({})
        loaded = database.load_schedule()
        self.assertEqual(loaded, {})
