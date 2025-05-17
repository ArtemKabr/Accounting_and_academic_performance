from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.input_file import BufferedInputFile
from src.utils.database import load_user_data, load_schedule, save_user_data, load_behavior_data
from datetime import datetime, timedelta
import io
import matplotlib.pyplot as plt

router = Router()

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

@router.message(lambda m: m.text == "📋 Мои данные")
async def show_parent_data(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data = load_user_data(user_id)
    if not user_data or user_data.get("role") != "Родитель":
        await message.answer("❌ Доступ только для родителей.")
        return

    msg = (
        f"📋 Ваши данные:\n"
        f"🆔 ID: {user_data['id']}\n"
        f"👤 ФИО: {user_data['fullname']}\n"
        f"📌 Роль: {user_data['role']}\n"
        f"👶 Ребёнок: {user_data['child_name']}\n"
        f"🔐 PIN-код: <code>{user_data['pin']}</code>"
    )
    await message.answer(msg, parse_mode="HTML")

@router.message(lambda m: m.text == "📅 Расписание")
async def parent_schedule(message: types.Message, state: FSMContext):
    user_data = load_user_data(str(message.from_user.id))
    if user_data and user_data.get("role") == "Родитель":
        await message.answer("📅 Выберите день недели:", reply_markup=days_of_week_keyboard())
    else:
        await message.answer("❌ Только для родителей.")

@router.message(lambda m: m.text in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"])
async def parent_day_schedule(message: types.Message, state: FSMContext):
    user_data = load_user_data(str(message.from_user.id))
    if user_data.get("role") != "Родитель":
        return

    schedule = load_schedule()
    lessons = schedule.get(message.text)
    if not lessons:
        await message.answer("❌ Нет расписания на этот день.")
        return

    msg = f"<b>{message.text}</b>\n" + "\n".join(f"• {l}" for l in lessons)
    await message.answer(msg, parse_mode="HTML", reply_markup=days_of_week_keyboard())

@router.message(lambda m: m.text == "📊 Поведение")
async def show_behavior(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data = load_user_data(user_id)
    if not user_data or user_data.get("role") != "Родитель":
        await message.answer("❌ Только для родителей.")
        return

    records = load_behavior_data()
    child_name = user_data.get("child_name").strip().lower()

    matches = [
        entry for entry in records
        if isinstance(entry, dict) and entry.get("ученик", "").strip().lower() == child_name
    ]
    if not matches:
        await message.answer(f"ℹ️ Поведение для {user_data['child_name']} не найдено.")
        return

    text = f"📊 Поведение ребёнка ({user_data['child_name']}):\n\n"
    for i, entry in enumerate(matches, 1):
        text += (
            f"{i}. 🗓 <b>{entry.get('дата', '—')}</b>\n"
            f"   📊 Оценка: {entry.get('оценка', '')}\n"
            f"   💬 Комментарий: {entry.get('комментарий', '')}\n\n"
        )
    await message.answer(text, parse_mode="HTML")

@router.message(lambda m: m.text == "📈 Статистика за неделю")
async def stats_week(message: types.Message, state: FSMContext):
    await show_behavior_stats(message, days=7)

@router.message(lambda m: m.text == "📊 Статистика за месяц")
async def stats_month(message: types.Message, state: FSMContext):
    await show_behavior_stats(message, days=30)

async def show_behavior_stats(message: types.Message, days: int):
    user_id = str(message.from_user.id)
    user_data = load_user_data(user_id)
    if not user_data or user_data.get("role") != "Родитель":
        await message.answer("❌ Только для родителей.")
        return

    records = load_behavior_data()
    child_name = user_data.get("child_name").strip().lower()
    now = datetime.now()

    scores = []
    labels = []

    for entry in records:
        if not isinstance(entry, dict):
            continue
        if entry.get("ученик", "").strip().lower() != child_name:
            continue
        try:
            dt = datetime.strptime(entry.get("дата", ""), "%Y-%m-%d %H:%M")
        except:
            continue
        if now - dt <= timedelta(days=days):
            score = convert_emoji_to_score(entry.get("оценка", ""))
            if score:
                scores.append(score)
                labels.append(dt.strftime("%d.%m"))

    if not scores:
        await message.answer("📭 Нет данных за выбранный период.")
        return

    # 📉 График
    fig, ax = plt.subplots()
    ax.plot(labels, scores, marker='o')
    ax.set_title(f"Оценки за {days} дней")
    ax.set_ylabel("Оценка")
    ax.set_ylim(0, 5.5)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    avg = round(sum(scores) / len(scores), 2)
    comment = generate_feedback(avg)

    image = BufferedInputFile(buf.read(), filename="stats.png")
    await message.answer_photo(photo=image, caption=f"📊 Средняя оценка: {avg}\n{comment}")

def convert_emoji_to_score(emoji: str) -> int | None:
    table = {
        "1️⃣": 1,
        "2️⃣": 2,
        "3️⃣": 3,
        "4️⃣": 4,
        "5️⃣": 5
    }
    return table.get(emoji.strip())

def generate_feedback(avg: float) -> str:
    if avg >= 4.5:
        return "🟢 Отличное поведение. Продолжайте в том же духе!"
    elif avg >= 3.5:
        return "🟡 В целом хорошо. Но возможны мелкие замечания."
    elif avg >= 2.5:
        return "🟠 Поведение нестабильно. Стоит обсудить с ребёнком."
    else:
        return "🔴 Часто низкие оценки. Рекомендуется обратить внимание."

@router.message(lambda m: m.text == "🔓 Выйти")
async def parent_logout(message: types.Message, state: FSMContext):
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
        if role == "Родитель":
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📋 Мои данные"), KeyboardButton(text="📅 Расписание")],
                    [KeyboardButton(text="📊 Поведение")],
                    [KeyboardButton(text="📈 Статистика за неделю"), KeyboardButton(text="📊 Статистика за месяц")],
                    [KeyboardButton(text="🔓 Выйти")]
                ],
                resize_keyboard=True
            )
            await message.answer("↩️ Главное меню:", reply_markup=keyboard)
            await state.clear()
