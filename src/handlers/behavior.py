from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.states.registration import Registration
from src.utils.database import load_user_data, save_behavior_data

router = Router()


# Начало — ввод имени ученика
@router.message(lambda m: m.text == "🧠 Оценить поведение")
async def start_behavior_rating(message: types.Message, state: FSMContext):
    user = load_user_data(str(message.from_user.id))
    if not user or user.get("role") != "Учитель":
        await message.answer("❌ Только для учителей.")
        return

    await message.answer("👶 Введите Фамилию Имя ученика, поведение которого хотите оценить:")
    await state.set_state(Registration.entering_behavior_name)


# Ввод имени ученика
@router.message(Registration.entering_behavior_name)
async def enter_behavior_name(message: types.Message, state: FSMContext):
    await state.update_data(behavior_name=message.text.strip())
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👍 Хорошо"), KeyboardButton(text="😐 Нормально"), KeyboardButton(text="👎 Плохо")]
        ],
        resize_keyboard=True
    )
    await message.answer("🧠 Выберите оценку поведения:", reply_markup=keyboard)
    await state.set_state(Registration.entering_behavior_rating)


# Выбор оценки
@router.message(Registration.entering_behavior_rating)
async def enter_behavior_rating(message: types.Message, state: FSMContext):
    if message.text not in ["👍 Хорошо", "😐 Нормально", "👎 Плохо"]:
        return await message.answer("Пожалуйста, выберите один из вариантов.")

    await state.update_data(behavior_rating=message.text)
    await message.answer("💬 Добавьте комментарий (по желанию):")
    await state.set_state(Registration.entering_behavior_comment)


# Ввод комментария
@router.message(Registration.entering_behavior_comment)
async def enter_behavior_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    behavior = {
        "ученик": data["behavior_name"],
        "оценка": data["behavior_rating"],
        "комментарий": message.text.strip()
    }

    save_behavior_data(behavior)

    msg = (
        f"✅ Оценка сохранена:\n"
        f"👶 Ученик: {behavior['ученик']}\n"
        f"🧠 Поведение: {behavior['оценка']}\n"
        f"💬 Комментарий: {behavior['комментарий']}"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

    await message.answer(msg, reply_markup=keyboard)
    await state.clear()

