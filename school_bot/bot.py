import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio

# Конфигурация
API_TOKEN = "7204660500:AAF9mD9F6q-_QkFaL9U_d6dW7mbZ2rRD-WY"
ADMIN_PASSWORD = "12345"
TEACHER_PASSWORD = "123"  # Пароль для учителей
USERS_DB_FILE = "users_db.json"
SCHEDULE_FILE = "schedule.json"

# Инициализация бота
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Состояния FSM
class RegistrationState(StatesGroup):
    choosing_role = State()
    waiting_for_password_parent = State()
    waiting_for_fio_parent = State()
    waiting_for_password_teacher = State()

# Загрузка данных с проверкой структуры
def load_users_db():
    if os.path.exists(USERS_DB_FILE):
        with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for user_id, user_data in data.items():
                if "role" not in user_data:
                    user_data["role"] = "parent"
                if "role_name" not in user_data:
                    user_data["role_name"] = "Родитель" if user_data["role"] == "parent" else "Учитель"
                if "access" not in user_data:
                    user_data["access"] = True
            return data
    return {}

def load_schedule():
    try:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Ошибка загрузки расписания: {e}")
        return {}

users_db = load_users_db()
schedule_storage = load_schedule()

# Клавиатуры
def get_role_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👪 Родитель", callback_data="role_parent")],
            [InlineKeyboardButton(text="👩‍🏫 Учитель", callback_data="role_teacher")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
        ]
    )

def get_back_keyboard(to_state: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_{to_state}")]
        ]
    )

def get_main_menu(role):
    buttons = [
        [InlineKeyboardButton(text="📅 Расписание", callback_data="show_schedule")]
    ]
    if role == "teacher":
        buttons.append([InlineKeyboardButton(text="✏️ Редактировать расписание", callback_data="edit_schedule")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Обработчики
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)

    if user_id in users_db:
        user_data = users_db[user_id]
        role = user_data.get("role", "parent")
        role_name = user_data.get("role_name", "Родитель" if role == "parent" else "Учитель")

        await message.answer(
            f"🔹 Вы авторизованы как {role_name}",
            reply_markup=get_main_menu(role)
        )
    else:
        await message.answer(
            "👋 Добро пожаловать! Выберите вашу роль:",
            reply_markup=get_role_keyboard()
        )
        await state.set_state(RegistrationState.choosing_role)

@dp.callback_query(RegistrationState.choosing_role)
async def process_role(callback: types.CallbackQuery, state: FSMContext):
    role = callback.data.replace("role_", "")

    if role == "parent":
        await callback.message.edit_text("🔒 Введите пароль для родителей:", reply_markup=get_back_keyboard("role"))
        await state.set_state(RegistrationState.waiting_for_password_parent)
    elif role == "teacher":
        await callback.message.edit_text("🔒 Введите пароль для учителей:", reply_markup=get_back_keyboard("role"))
        await state.set_state(RegistrationState.waiting_for_password_teacher)

    await callback.answer()

@dp.message(RegistrationState.waiting_for_password_parent)
async def check_parent_password(message: types.Message, state: FSMContext):
    if message.text.strip() == ADMIN_PASSWORD:
        await message.answer("✅ Пароль верный! Теперь введите ваше ФИО:", reply_markup=get_back_keyboard("parent_password"))
        await state.set_state(RegistrationState.waiting_for_fio_parent)
    else:
        await message.answer("❌ Неверный пароль. Попробуйте снова.", reply_markup=get_back_keyboard("role"))

@dp.message(RegistrationState.waiting_for_fio_parent)
async def save_parent(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    fio = message.text.strip()

    users_db[user_id] = {
        "fio": fio,
        "role": "parent",
        "role_name": "Родитель",
        "access": True
    }

    try:
        with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users_db, f, ensure_ascii=False, indent=2)
        await message.answer(
            f"👪 Регистрация родителя {fio} завершена!",
            reply_markup=get_main_menu("parent")
        )
    except Exception as e:
        await message.answer("❌ Ошибка сохранения данных. Попробуйте позже.")
        print(f"Ошибка сохранения: {e}")

    await state.clear()

@dp.message(RegistrationState.waiting_for_password_teacher)
async def check_teacher_password(message: types.Message, state: FSMContext):
    if message.text.strip() == TEACHER_PASSWORD:
        user_id = str(message.from_user.id)

        users_db[user_id] = {
            "role": "teacher",
            "role_name": "Учитель",
            "access": True
        }

        try:
            with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(users_db, f, ensure_ascii=False, indent=2)
            await message.answer(
                "👩‍🏫 Вы успешно авторизованы как учитель!",
                reply_markup=get_main_menu("teacher")
            )
        except Exception as e:
            await message.answer("❌ Ошибка сохранения данных. Попробуйте позже.")
            print(f"Ошибка сохранения: {e}")

        await state.clear()
    else:
        await message.answer("❌ Неверный пароль. Попробуйте снова.", reply_markup=get_back_keyboard("role"))

@dp.callback_query(lambda c: c.data.startswith("back_"))
async def handle_back(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.replace("back_", "")

    if action == "role":
        await callback.message.edit_text("👋 Выберите вашу роль:", reply_markup=get_role_keyboard())
        await state.set_state(RegistrationState.choosing_role)
    elif action == "parent_password":
        await callback.message.edit_text("🔒 Введите пароль для родителей:", reply_markup=get_back_keyboard("role"))
        await state.set_state(RegistrationState.waiting_for_password_parent)

    await callback.answer()

@dp.callback_query(lambda c: c.data == "show_schedule")
async def show_schedule_handler(callback: types.CallbackQuery):
    try:
        global schedule_storage
        schedule_storage = load_schedule()

        if not schedule_storage:
            await callback.answer("Расписание не загружено", show_alert=True)
            return

        days = list(schedule_storage.keys())
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=day, callback_data=f"day_{day}")]
                for day in days
            ]
        )

        await callback.message.edit_text(
            "📅 Выберите день недели:",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка в show_schedule_handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)
    finally:
        await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("day_"))
async def show_day_schedule(callback: types.CallbackQuery):
    try:
        day = callback.data[4:]
        global schedule_storage
        schedule_storage = load_schedule()

        if day not in schedule_storage:
            await callback.answer("День не найден", show_alert=True)
            return

        subjects = schedule_storage[day]
        response = f"📅 Расписание на <b>{day}</b>:\n" + \
                   "\n".join(f"{i}. {subj}" for i, subj in enumerate(subjects, 1))

        await callback.message.edit_text(
            response,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="← Назад",
                        callback_data="show_schedule"
                    )]
                ]
            )
        )
    except Exception as e:
        print(f"Ошибка в show_day_schedule: {e}")
        await callback.answer("Ошибка загрузки расписания", show_alert=True)
    finally:
        await callback.answer()

def get_days_keyboard():
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *[[InlineKeyboardButton(text=day, callback_data=f"day_{day}")] for day in days],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
        ]
    )
    return keyboard

@dp.callback_query(lambda c: c.data == "main_menu")
async def handle_main_menu(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    if user_id in users_db:
        role = users_db[user_id].get("role", "parent")
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=get_main_menu(role)
        )
    await callback.answer()

# Запуск бота
async def main():
    print("Бот запущен!")
    print("Загруженные пользователи:", users_db)
    print("Загруженное расписание:", schedule_storage)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())