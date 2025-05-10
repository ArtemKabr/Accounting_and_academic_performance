# Кнопки \"назад\" и главное меню.

from aiogram import types
from aiogram.fsm.context import FSMContext
from src.states.registration import RegistrationState
from src.keyboards.inline import get_role_keyboard, get_main_menu

@dp.callback_query(lambda c: c.data.startswith("back_"))
async def handle_back(callback: types.CallbackQuery, state: FSMContext):
    # ... код обработки навигации ...