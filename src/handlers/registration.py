# Состояния регистрации.

from aiogram import types
from aiogram.fsm.context import FSMContext
from src.states.registration import RegistrationState
from src.keyboards.inline import get_back_keyboard, get_main_menu
from src.utils.database import load_users_db, save_users_db
from config import ADMIN_PASSWORD, TEACHER_PASSWORD

users_db = load_users_db()

@dp.callback_query(RegistrationState.choosing_role)
async def process_role(callback: types.CallbackQuery, state: FSMContext):
    role = callback.data.replace("role_", "")
    # ... остальной код обработчиков регистрации ...
