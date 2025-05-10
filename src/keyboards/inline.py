# Инлайн-кнопки.

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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

def get_days_keyboard():
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *[[InlineKeyboardButton(text=day, callback_data=f"day_{day}")] for day in days],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
        ]
    )