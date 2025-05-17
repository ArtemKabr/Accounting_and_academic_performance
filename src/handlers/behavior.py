from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.states.registration import Registration
from src.utils.database import load_user_data, append_behavior_entry

router = Router()

# 🧠 Начало: оценка поведения
@router.message(lambda m: m.text == "🧠 Оценить поведение")
async def start_behavior_rating(message: types.Message, state: FSMContext):
    user = load_user_data(str(message.from_user.id))
    if not user or user.get("role") != "Учитель":
        await message.answer("❌ Только для учителей.")
        return

    await message.answer("👶 Введите Фамилию Имя ученика, поведение которого хотите оценить:")
    await state.set_state(Registration.entering_behavior_name)

# 👶 Ввод ФИО ученика
@router.message(Registration.entering_behavior_name)
async def enter_behavior_name(message: types.Message, state: FSMContext):
    await state.update_data(behavior_name=message.text.strip())

    # 🔢 Клавиатура с 5-балльной системой
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="1️⃣"), KeyboardButton(text="2️⃣"),
            KeyboardButton(text="3️⃣"), KeyboardButton(text="4️⃣"),
            KeyboardButton(text="5️⃣")
        ]],
        resize_keyboard=True
    )
    await message.answer("🧠 Поставьте оценку от 1 до 5:", reply_markup=keyboard)
    await state.set_state(Registration.entering_behavior_rating)

# 🧠 Выбор оценки
@router.message(Registration.entering_behavior_rating)
async def enter_behavior_rating(message: types.Message, state: FSMContext):
    if message.text not in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]:
        return await message.answer("Пожалуйста, выберите оценку от 1️⃣ до 5️⃣.")

    await state.update_data(behavior_rating=message.text)
    await message.answer("💬 Добавьте комментарий:")
    await state.set_state(Registration.entering_behavior_comment)

# 💬 Ввод комментария и сохранение
@router.message(Registration.entering_behavior_comment)
async def enter_behavior_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    behavior = {
        "ученик": data["behavior_name"],
        "оценка": data["behavior_rating"],  # будет "1️⃣", "2️⃣" и т.д.
        "комментарий": message.text.strip()
    }

    append_behavior_entry(behavior)

    msg = (
        f"✅ Оценка сохранена:\n"
        f"👶 Ученик: {behavior['ученик']}\n"
        f"📊 Оценка: {behavior['оценка']}\n"
        f"💬 Комментарий: {behavior['комментарий']}"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True
    )

    await message.answer(msg, reply_markup=keyboard)
    await state.clear()
