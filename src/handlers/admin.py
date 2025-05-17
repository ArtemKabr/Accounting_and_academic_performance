import os
import io
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, BufferedInputFile
from src.handlers.start import admin_menu_keyboard
from src.states.registration import Registration
from src.utils.database import DB_FILE, BEHAVIOR_FILE

router = Router()

# Клавиатура отмены

def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Отмена")]],
        resize_keyboard=True
    )

# Отмена рассылки

@router.message(Registration.entering_broadcast_text, lambda m: m.text == "🔙 Отмена")
async def cancel_broadcast(message: types.Message, state: FSMContext):
    await message.answer("❌ Рассылка отменена.", reply_markup=admin_menu_keyboard())
    await state.clear()

# Общая статистика

@router.message(lambda m: m.text == "📈 Статистика")
async def show_statistics(message: types.Message):
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except:
        users = {}

    total = len(users)
    roles = {"Родитель": 0, "Учитель": 0, "Администратор": 0}
    children = 0

    for u in users.values():
        role = u.get("role")
        if role in roles:
            roles[role] += 1
        if role == "Родитель" and u.get("child_name"):
            children += 1

    try:
        with open(BEHAVIOR_FILE, "r", encoding="utf-8") as f:
            behavior_data = json.load(f)
            behavior_count = len(behavior_data)
    except:
        behavior_count = 0

    msg = (
        "<b>📈 Общая статистика:</b>\n\n"
        f"👥 Всего пользователей: <b>{total}</b>\n"
        f"— Родителей: <b>{roles['Родитель']}</b>\n"
        f"— Учителей: <b>{roles['Учитель']}</b>\n"
        f"— Админов: <b>{roles['Администратор']}</b>\n"
        f"👶 Ученики: <b>{children}</b>\n"
        f"🧠 Записей поведения: <b>{behavior_count}</b>"
    )

    await message.answer(msg, parse_mode="HTML")

# График поведения

@router.message(lambda m: m.text == "📉 График поведения")
async def behavior_chart(message: types.Message):
    behavior_path = "src/data/behavior.json"

    if not os.path.exists(behavior_path):
        return await message.answer("⚠️ Поведение ещё не зафиксировано.")

    with open(behavior_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            return await message.answer("⚠️ Ошибка чтения файла поведения.")

    scores_by_child = {}
    for entry in data:
        name = entry.get("ученик", "—").strip()
        emoji = entry.get("оценка", "").strip()
        score = convert_emoji_to_score(emoji)
        if not score:
            continue
        scores_by_child.setdefault(name, []).append(score)

    if not scores_by_child:
        return await message.answer("❌ Нет оценок, пригодных для анализа.")

    names = []
    avgs = []
    colors = []
    for name, values in scores_by_child.items():
        avg = round(sum(values) / len(values), 2)
        names.append(name)
        avgs.append(avg)
        if avg <= 1:
            colors.append("#FF0000")
        elif avg <= 2:
            colors.append("#00EEEE")
        elif avg <= 3:
            colors.append("#FFFF00")
        elif avg <= 4:
            colors.append("#FF00FF")
        else:
            colors.append("#00FF00")

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(names, avgs, color=colors)
    ax.set_title("Средняя оценка по каждому ученику")
    ax.set_ylabel("Оценка (1–5)")
    ax.set_ylim(0, 5.5)
    plt.xticks(rotation=90, fontsize=12)

    legend_elements = [
        Patch(facecolor="#FF0000", label="1"),
        Patch(facecolor="#00EEEE", label="2"),
        Patch(facecolor="#FFFF00", label="3"),
        Patch(facecolor="#FF00FF", label="4"),
        Patch(facecolor="#00FF00", label="5")
    ]

    ax.legend(handles=legend_elements, title="Оценки", loc="best")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    await message.answer_photo(photo=BufferedInputFile(buf.read(), filename="behavior_chart.png"), caption="📉 Статистика по поведению всех учеников")

# Перевод смайла в цифру

def convert_emoji_to_score(emoji: str) -> int | None:
    return {
        "1️⃣": 1,
        "2️⃣": 2,
        "3️⃣": 3,
        "4️⃣": 4,
        "5️⃣": 5
    }.get(emoji)

# 📢 Массовая рассылка
@router.message(lambda m: m.text == "📢 Массовая рассылка")
async def ask_broadcast_text(message: types.Message, state: FSMContext):
    await message.answer(
        "✍️ Введите текст сообщения для рассылки:\n\nИли нажмите 🔙 Отмена, чтобы выйти.",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(Registration.entering_broadcast_text)


@router.message(Registration.entering_broadcast_text)
async def send_broadcast(message: types.Message, state: FSMContext):
    text = message.text.strip()

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except Exception:
        return await message.answer("⚠️ Не удалось загрузить базу пользователей.")

    count = 0
    for user_id in users:
        try:
            await message.bot.send_message(
                chat_id=user_id,
                text=f"📢 <b>Сообщение от администрации</b>:\n\n{text}",
                parse_mode="HTML"
            )
            count += 1
        except:
            continue

    await message.answer(f"✅ Сообщение успешно отправлено {count} пользователям.")
    await state.clear()


# 📊 Пользователи
@router.message(lambda m: m.text == "📊 Пользователи")
async def show_all_users(message: types.Message):
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except Exception:
        return await message.answer("❌ Не удалось загрузить базу пользователей.")

    if not users:
        return await message.answer("ℹ️ Пользователей пока нет.")

    text = "📋 <b>Список пользователей:</b>\n\n"
    for u in users.values():
        role = u.get("role", "—")
        name = u.get("fullname", "—")
        child = u.get("child_name", "") if role == "Родитель" else ""
        pin = u.get("pin", "—")
        text += f"👤 {name} ({role})\n🔐 PIN: <code>{pin}</code>\n"
        if child:
            text += f"👶 Ребёнок: {child}\n"
        text += "\n"

    await message.answer(text, parse_mode="HTML")


# 📚 Поведение всех учеников
@router.message(lambda m: m.text == "📚 Поведение всех учеников")
async def show_all_behavior(message: types.Message):
    if not os.path.exists(BEHAVIOR_FILE):
        return await message.answer("📁 Файл с поведением не найден.")

    try:
        with open(BEHAVIOR_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    except Exception:
        return await message.answer("⚠️ Ошибка при чтении данных.")

    if not records:
        return await message.answer("ℹ️ Поведение пока не зафиксировано.")

    text = "<b>📚 Поведение всех учеников:</b>\n\n"
    for i, entry in enumerate(records, 1):
        text += (
            f"{i}. 👶 <b>{entry.get('ученик', '—')}</b>\n"
            f"   🧠 {entry.get('оценка', '')}\n"
            f"   💬 {entry.get('комментарий', '')}\n"
            f"   📅 {entry.get('дата', '—')}\n\n"
        )

    await message.answer(text, parse_mode="HTML")
