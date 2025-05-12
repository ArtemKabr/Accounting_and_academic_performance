from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from src.states.registration import Registration
from src.utils.database import save_user_data
import uuid

router = Router()

PARENT_PASSWORD = "1234"
TEACHER_PASSWORD = "4321"

def nav_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )

def main_menu_keyboard(role):
    buttons = [
        [KeyboardButton(text="📋 Мои данные"), KeyboardButton(text="📅 Расписание")],
        [KeyboardButton(text="🔓 Выйти")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ▶️ /start
@router.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Учитель"), KeyboardButton(text="Родитель")]],
        resize_keyboard=True
    )
    await message.answer("Выберите роль:", reply_markup=keyboard)
    await state.set_state(Registration.choosing_role)

# 🔸 Выбор роли
@router.message(Registration.choosing_role)
async def choose_role(message: types.Message, state: FSMContext):
    if message.text not in ["Учитель", "Родитель"]:
        return await message.answer("Пожалуйста, выберите: Учитель или Родитель.")
    await state.update_data(role=message.text)
    await message.answer("🔑 Введите пароль для вашей роли:", reply_markup=nav_keyboard())
    await state.set_state(Registration.entering_password)

# 🔐 Проверка пароля
@router.message(Registration.entering_password)
async def verify_password(message: types.Message, state: FSMContext):
    user_input = message.text.strip()
    data = await state.get_data()
    role = data.get("role")

    if (role == "Учитель" and user_input == TEACHER_PASSWORD) or \
       (role == "Родитель" and user_input == PARENT_PASSWORD):
        await message.answer("✍️ Введите ваше ФИО:")
        await state.set_state(Registration.entering_fullname)
    else:
        await message.answer("❌ Неверный пароль. Попробуйте снова.")

# 🧾 Ввод ФИО
@router.message(Registration.entering_fullname)
async def enter_fullname(message: types.Message, state: FSMContext):
    fullname = message.text.strip()
    await state.update_data(fullname=fullname)
    data = await state.get_data()

    if data.get("role") == "Родитель":
        await message.answer("👶 Введите ФИО вашего ребёнка:")
        await state.set_state(Registration.entering_child_name)
    else:
        await finish_registration(message, state)

# 👶 Ребёнок
@router.message(Registration.entering_child_name)
async def enter_child_name(message: types.Message, state: FSMContext):
    child_name = message.text.strip()
    await state.update_data(child_name=child_name)
    await finish_registration(message, state)

# ✅ Завершение
async def finish_registration(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = str(message.from_user.id)
    user_uuid = str(uuid.uuid4())

    user_data = {
        "id": user_uuid,
        "telegram_id": user_id,
        "fullname": data.get("fullname"),
        "role": data.get("role"),
        "authenticated": True
    }

    if data["role"] == "Родитель":
        user_data["child_name"] = data.get("child_name")

    save_user_data(user_id, user_data)

    msg = (
        f"🎉 Регистрация завершена!\n"
        f"🆔 ID: {user_uuid}\n"
        f"👤 ФИО: {user_data['fullname']}\n"
        f"📌 Роль: {user_data['role']}"
    )
    if user_data["role"] == "Родитель":
        msg += f"\n👶 Ребёнок: {user_data['child_name']}"

    await message.answer(msg, reply_markup=main_menu_keyboard(user_data["role"]))
    await state.clear()
