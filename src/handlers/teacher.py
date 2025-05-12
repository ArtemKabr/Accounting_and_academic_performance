from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.utils.database import load_user_data, load_schedule, save_user_data

router = Router()

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

# 📅 Просмотр расписания (доступ только для учителей)
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

@router.message(lambda m: m.text == "🔙 Назад")
async def handle_back_to_menu(message: types.Message, state: FSMContext):
    user = load_user_data(str(message.from_user.id))
    if user:
        role = user.get("role")
        if role == "Учитель" or role == "Родитель":
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📋 Мои данные"), KeyboardButton(text="📅 Расписание")],
                    [KeyboardButton(text="🔓 Выйти")]
                ],
                resize_keyboard=True
            )
            await message.answer("↩️ Главное меню:", reply_markup=keyboard)
            await state.clear()
