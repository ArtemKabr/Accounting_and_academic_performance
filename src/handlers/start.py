from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from src.states.registration import Registration
from src.utils.database import save_user_data, load_user_data
import uuid
import random

router = Router()

ADMIN_PIN = "22059"  # можешь изменить
PARENT_PASSWORD = "1234"
TEACHER_PIN = "4321"  # постоянный PIN учителя

# 🔘 Клавиатуры
# 🔘 Клавиатуры
def role_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Учитель"), KeyboardButton(text="Родитель")],
            [KeyboardButton(text="Администратор")]
        ],
        resize_keyboard=True
    )

def yes_no_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )


def nav_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )

def main_menu_keyboard(role):
    if role == "Учитель":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📋 Мои данные"), KeyboardButton(text="📅 Расписание")],
                [KeyboardButton(text="🧠 Оценить поведение"), KeyboardButton(text="📢 Доска сообщений")],
                [KeyboardButton(text="🔓 Выйти")]
            ],
            resize_keyboard=True
        )
    elif role == "Родитель":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📋 Мои данные"), KeyboardButton(text="📅 Расписание")],
                [KeyboardButton(text="📊 Поведение")],
                [KeyboardButton(text="📈 Статистика за неделю"), KeyboardButton(text="📊 Статистика за месяц")],
                [KeyboardButton(text="🔓 Выйти")]
            ],
            resize_keyboard=True
        )
    elif role == "Администратор":
        return admin_menu_keyboard()  # возвращаем админ-клавиатуру отдельно

def admin_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Пользователи")],
            [KeyboardButton(text="📢 Массовая рассылка")],
            [KeyboardButton(text="📚 Поведение всех учеников")],
            [KeyboardButton(text="📈 Статистика"), KeyboardButton(text="📉 График поведения")],
            [KeyboardButton(text="🔓 Выйти")]
        ],
        resize_keyboard=True
    )


# ▶️ /start
@router.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await message.answer("👤 Кто вы?", reply_markup=role_keyboard())
    await state.set_state(Registration.choosing_role)


@router.message(lambda m: m.text == "🔙 Назад")
async def back_to_last_place(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last = data.get("last_menu")

    if last == "choose_registration_path":
        await message.answer("Вы уже зарегистрированы?", reply_markup=yes_no_keyboard())
        await state.set_state(Registration.choosing_registration_path)

    elif last == "parent_menu":
        await message.answer("↩️ Главное меню родителя:", reply_markup=main_menu_keyboard("Родитель"))
        await state.clear()

    elif last == "teacher_menu":
        await message.answer("↩️ Главное меню учителя:", reply_markup=main_menu_keyboard("Учитель"))
        await state.clear()

    elif last == "admin_menu":
        await message.answer("↩️ Главное меню администратора:", reply_markup=main_menu_keyboard("Администратор"))
        await state.clear()

    else:
        await message.answer("👤 Кто вы?", reply_markup=role_keyboard())
        await state.set_state(Registration.choosing_role)



# 🔸 Выбор роли
@router.message(Registration.choosing_role)
async def choose_role(message: types.Message, state: FSMContext):
    role = message.text.strip()
    if role not in ["Учитель", "Родитель", "Администратор"]:
        return await message.answer("Пожалуйста, выберите: Учитель, Родитель или Администратор.")

    await state.update_data(role=role)

    if role == "Учитель":
        await message.answer("🔐 Введите PIN-код для входа (статический):")
        await state.set_state(Registration.entering_teacher_pin)

    elif role == "Администратор":
        await message.answer("🔐 Введите PIN администратора:")
        await state.set_state(Registration.entering_admin_pin)

    else:
        await message.answer("Вы уже зарегистрированы?", reply_markup=yes_no_keyboard())
        await state.set_state(Registration.choosing_registration_path)


# 🔑 Ввод PIN учителя
@router.message(Registration.entering_teacher_pin)
async def teacher_login(message: types.Message, state: FSMContext):
    if message.text.strip() == TEACHER_PIN:
        user_id = str(message.from_user.id)

        # 🔒 Проверка: уже зарегистрирован?
        existing = load_user_data(user_id)
        if existing:
            await state.update_data(last_menu="teacher_menu")
            await message.answer("❗ Вы уже зарегистрированы как учитель или родитель.")
            return

        # ✅ Регистрируем учителя
        user_data = {
            "id": user_id,
            "telegram_id": user_id,
            "fullname": "Учитель",
            "role": "Учитель",
            "authenticated": True,
            "pin": TEACHER_PIN
        }
        save_user_data(user_id, user_data)
        await message.answer("✅ Вход выполнен как учитель.", reply_markup=main_menu_keyboard("Учитель"))
        await state.clear()
    else:
        await message.answer("❌ Неверный PIN. Попробуйте снова.")

# ✅ Регистрируем Админа
@router.message(Registration.entering_admin_pin)
async def admin_login(message: types.Message, state: FSMContext):
    if message.text.strip() == ADMIN_PIN:
        user_id = str(message.from_user.id)

        user_data = {
            "id": user_id,
            "telegram_id": user_id,
            "fullname": "Администратор",
            "role": "Администратор",
            "authenticated": True,
            "pin": ADMIN_PIN
        }

        save_user_data(user_id, user_data)
        await state.update_data(last_menu="admin_menu")
        await message.answer("✅ Вход выполнен как администратор.", reply_markup=admin_menu_keyboard())
        await state.clear()
    else:
        await message.answer("❌ Неверный PIN администратора.")


# 🔸 РОДИТЕЛЬ: Зарегистрирован ли
@router.message(Registration.choosing_registration_path)
async def handle_parent_registration_choice(message: types.Message, state: FSMContext):
    if message.text == "✅ Да":
        await message.answer("🔐 Введите ваш PIN-код:")
        await state.set_state(Registration.entering_password)
    elif message.text == "❌ Нет":
        await message.answer("✍️ Введите ваше ФИО:", reply_markup=nav_keyboard())
        await state.set_state(Registration.entering_fullname)
    else:
        await message.answer("Пожалуйста, выберите ✅ Да или ❌ Нет.")

# 🔐 Ввод PIN для родителя
@router.message(Registration.entering_password)
async def check_parent_pin(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data = load_user_data(user_id)
    input_pin = message.text.strip()

    if not user_data or user_data.get("role") != "Родитель":
        await state.update_data(last_menu="choose_registration_path")
        await message.answer("❌ Вы не зарегистрированы. Пройдите регистрацию.")
        await state.clear()
        return

    if input_pin == user_data.get("pin"):
        user_data["authenticated"] = True
        save_user_data(user_id, user_data)
        await message.answer("✅ Вход выполнен!", reply_markup=main_menu_keyboard("Родитель"))
        await state.clear()
    else:
        await message.answer("❌ Неверный PIN. Попробуйте снова.")

# 🧾 Ввод ФИО родителя
@router.message(Registration.entering_fullname)
async def enter_fullname(message: types.Message, state: FSMContext):
    fullname = message.text.strip()
    await state.update_data(fullname=fullname)
    await message.answer("👶 Введите ФИ вашего ребёнка:")
    await state.set_state(Registration.entering_child_name)

# 👶 Ввод ФИО ребёнка
@router.message(Registration.entering_child_name)
async def enter_child_name(message: types.Message, state: FSMContext):
    child_name = message.text.strip()
    await state.update_data(child_name=child_name)

    data = await state.get_data()
    user_id = str(message.from_user.id)
    user_uuid = str(uuid.uuid4())
    pin_code = str(random.randint(1000, 9999))

    user_data = {
        "id": user_uuid,
        "telegram_id": user_id,
        "fullname": data["fullname"],
        "child_name": data["child_name"],
        "role": "Родитель",
        "authenticated": True,
        "pin": pin_code
    }

    save_user_data(user_id, user_data)

    msg = (
        f"🎉 Регистрация завершена!\n"
        f"🆔 ID: {user_uuid}\n"
        f"🔐 Ваш PIN: <code>{pin_code}</code>\n"
        f"👤 ФИО: {data['fullname']}\n"
        f"👶 Ребёнок: {data['child_name']}\n"
        f"📌 Роль: Родитель"
    )
    await message.answer(msg, parse_mode="HTML", reply_markup=main_menu_keyboard("Родитель"))
    await state.clear()
