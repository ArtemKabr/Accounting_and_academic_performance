# Просмотр расписания.

from aiogram import types
from src.utils.database import load_schedule
from src.keyboards.inline import get_days_keyboard

@dp.callback_query(lambda c: c.data == "show_schedule")
async def show_schedule_handler(callback: types.CallbackQuery):
    # ... код обработчиков расписания ...