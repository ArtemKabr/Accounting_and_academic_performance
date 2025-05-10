from src.keyboards.inline import get_role_keyboard, get_main_menu  # Один импорт, удалите дублирующийся
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command  # Правильный импорт для Command в aiogram 3.x
from loader import dp
from src.utils.database import load_users_db
from aiogram.fsm.state import State  # Импорт состояния
from aiogram.fsm.context import FSMContext  # Импорт FSMContext для работы с состояниями

# Загрузим данные из базы пользователей
users_db = load_users_db()

# Определим состояния для регистрации
class RegistrationState(State):
    choosing_role = "choosing_role"  # Пример состояния

# Обработчик для команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)

    # Проверка, если пользователь есть в базе данных
    if user_id in users_db:
        user_data = users_db[user_id]
        role = user_data.get("role", "parent")  # Определение роли пользователя
        await message.answer(
            f"🔹 Вы авторизованы как {user_data.get('role_name', 'Родитель' if role == 'parent' else 'Учитель')}",
            reply_markup=get_main_menu(role)  # Отправка клавиатуры в зависимости от роли
        )
    else:
        # Если пользователя нет в базе, предложим выбрать роль
        await message.answer(
            "👋 Добро пожаловать! Выберите вашу роль:",
            reply_markup=get_role_keyboard()  # Отправка клавиатуры для выбора роли
        )
        # Устанавливаем состояние для выбора роли
        await state.set_state(RegistrationState.choosing_role)
