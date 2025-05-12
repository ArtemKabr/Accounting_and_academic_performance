from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    choosing_role = State()
    choosing_registration_path = State()
    entering_role_password = State()
    entering_teacher_pin = State()  # ← Добавь вот это
    entering_password = State()
    entering_fullname = State()
    entering_child_name = State()
    choosing_schedule_day = State()
    entering_schedule = State()
    entering_behavior_name = State()
    entering_behavior_rating = State()
    entering_behavior_comment = State()



