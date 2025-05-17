import os
import json
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from src.utils.database import load_user_data, load_schedule, save_user_data, DB_FILE

router = Router()

# Состояние для экстренной рассылки
class EmergencyBoard(StatesGroup):
    waiting_for_message = State()

# 📅 Клавиатура с днями недели
def days_of_week_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Понедельник"), KeyboardButton(text="Вторник")],
            [KeyboardButton(text="Среда"), KeyboardButton(text="Четверг")],
            [KeyboardButton(text="Пятница")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

# 📋 Мои данные (учитель)
@router.message(lambda m: m.text == "📋 Мои данные")
async def show_teacher_data(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data = load_user_data(user_id)
    if not user_data or user_data.get("role") != "Учитель":
        await message.answer("❌ Доступ только для учителей.")
        return

    msg = (
        f"📋 Ваши данные:\n"
        f"🆔 ID: {user_data['id']}\n"
        f"👤 ФИО: {user_data['fullname']}\n"
        f"📌 Роль: {user_data['role']}"
    )
    await message.answer(msg)

# 📅 Просмотр расписания
@router.message(lambda m: m.text == "📅 Расписание")
async def teacher_schedule_view(message: types.Message, state: FSMContext):
    user_data = load_user_data(str(message.from_user.id))
    if user_data and user_data.get("role") == "Учитель":
        await message.answer("📅 Выберите день недели:", reply_markup=days_of_week_keyboard())
    else:
        await message.answer("❌ Доступ только для учителей.")

# 📅 Конкретный день
@router.message(lambda m: m.text in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"])
async def teacher_day_schedule(message: types.Message, state: FSMContext):
    user_data = load_user_data(str(message.from_user.id))
    if user_data.get("role") != "Учитель":
        return

    schedule = load_schedule()
    lessons = schedule.get(message.text)
    if not lessons:
        await message.answer("❌ Нет расписания на этот день.")
        return

    msg = f"📅 <b>{message.text}</b>\n" + "\n".join(f"• {l}" for l in lessons)
    await message.answer(msg, parse_mode="HTML", reply_markup=days_of_week_keyboard())

# 🔓 Выйти
@router.message(lambda m: m.text == "🔓 Выйти")
async def teacher_logout(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data = load_user_data(user_id)
    if user_data:
        user_data["authenticated"] = False
        save_user_data(user_id, user_data)

    await message.answer("Вы вышли. Нажмите /start для входа заново.")
    await state.clear()

# 📢 Экстренная доска сообщений — старт
@router.message(lambda m: m.text == "📢 Доска сообщений")
async def start_emergency_board(message: types.Message, state: FSMContext):
    user = load_user_data(str(message.from_user.id))
    if not user or user.get("role") != "Учитель":
        await message.answer("❌ Только для учителей.")
        return

    await message.answer("✍️ Введите сообщение, которое будет разослано всем пользователям:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(EmergencyBoard.waiting_for_message)

# 📢 Экстренная доска сообщений — отправка
@router.message(EmergencyBoard.waiting_for_message)
async def send_emergency_to_all(message: types.Message, state: FSMContext):
    text = message.text.strip()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except Exception:
        await message.answer("⚠️ Не удалось загрузить список пользователей.")
        return

    count = 0
    for user_id in users:
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text=f"📢 <b>Экстренное сообщение от учителя</b>:\n\n{text}",
                parse_mode="HTML"
            )
            count += 1
        except Exception:
            continue

    await message.answer(f"✅ Сообщение разослано {count} пользователям.")
    await state.clear()

# 🔙 Назад в меню
@router.message(lambda m: m.text == "🔙 Назад")
async def handle_back_to_menu(message: types.Message, state: FSMContext):
    user = load_user_data(str(message.from_user.id))
    if user and user.get("role") == "Учитель":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📋 Мои данные"), KeyboardButton(text="📅 Расписание")],
                [KeyboardButton(text="📢 Доска сообщений")],
                [KeyboardButton(text="🔓 Выйти")]
            ],
            resize_keyboard=True
        )
        await message.answer("↩️ Главное меню:", reply_markup=keyboard)
        await state.clear()

# /поведение <ФИО>
@router.message(lambda m: m.text.lower().startswith("/поведение"))
async def show_behavior_for_student(message: types.Message):
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) != 2:
        return await message.answer("Введите ФИО ученика: /поведение Иванов Иван")

    query_name = parts[1].strip().lower()
    path = "src/database/behavior.json"

    if not os.path.exists(path):
        return await message.answer("📁 Поведение не зафиксировано.")

    with open(path, "r", encoding="utf-8") as f:
        try:
            records = json.load(f)
        except json.JSONDecodeError:
            return await message.answer("⚠️ Ошибка чтения файла.")

    matches = [
        entry for entry in records
        if entry.get("ученик", "").strip().lower() == query_name
    ]

    if not matches:
        return await message.answer(f"❌ Нет данных для ученика {query_name}")

    text = f"📊 Поведение ученика: {query_name}\n\n"
    for i, entry in enumerate(matches, 1):
        text += (
            f"{i}. 🗓 {entry.get('дата', '—')}\n"
            f"   🧠 {entry.get('оценка', '')}\n"
            f"   💬 {entry.get('комментарий', '')}\n\n"
        )

    await message.answer(text)
