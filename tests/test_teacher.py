import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from src.utils.database import save_user_data, load_user_data

class TestTeacherLogic(unittest.TestCase):

    def setUp(self):
        self.teacher_id = "test_teacher"
        self.teacher_data = {
            "id": "uuid123",
            "telegram_id": self.teacher_id,
            "fullname": "Учитель Учительский",
            "role": "Учитель",
            "authenticated": True
        }

    def test_teacher_registration(self):
        save_user_data(self.teacher_id, self.teacher_data)
        loaded = load_user_data(self.teacher_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["role"], "Учитель")
        self.assertTrue(loaded["authenticated"])
        self.assertEqual(loaded["fullname"], "Учитель Учительский")

    def test_teacher_logout(self):
        self.teacher_data["authenticated"] = False
        save_user_data(self.teacher_id, self.teacher_data)
        loaded = load_user_data(self.teacher_id)
        self.assertFalse(loaded["authenticated"])
