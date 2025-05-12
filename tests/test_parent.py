import unittest
import os
import json
from src.utils.database import save_user_data, load_user_data, save_schedule, load_schedule

class ParentModuleTest(unittest.TestCase):

    def setUp(self):
        # Очистка данных перед каждым тестом
        self.user_id = "1111"
        self.schedule_day = "Понедельник"

        # Сохраняем родителя
        self.parent_data = {
            "id": "abc123",
            "telegram_id": self.user_id,
            "fullname": "Иванова Мария",
            "role": "Родитель",
            "child_name": "Иванов Петя",
            "authenticated": True
        }
        save_user_data(self.user_id, self.parent_data)

        # Сохраняем расписание
        self.test_schedule = {
            self.schedule_day: ["Математика", "Русский язык", "Окружающий мир"]
        }
        save_schedule(self.test_schedule)

    def test_load_parent_user(self):
        user = load_user_data(self.user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "Родитель")
        self.assertEqual(user["child_name"], "Иванов Петя")

    def test_schedule_loading(self):
        schedule = load_schedule()
        self.assertIn(self.schedule_day, schedule)
        self.assertEqual(schedule[self.schedule_day][0], "Математика")

    def test_non_parent_access_block(self):
        another_id = "9999"
        non_parent = {
            "id": "x456",
            "telegram_id": another_id,
            "fullname": "Учитель Иван",
            "role": "Учитель",
            "authenticated": True
        }
        save_user_data(another_id, non_parent)
        user = load_user_data(another_id)
        self.assertEqual(user["role"], "Учитель")

if __name__ == '__main__':
    unittest.main()
