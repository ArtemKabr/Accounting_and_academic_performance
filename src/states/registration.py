from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    choosing_role = State()
    choose_login_or_register = State()
    entering_fullname = State()
    entering_child_name = State()
    entering_password = State()
    choosing_schedule_day = State()
    choosing_edit_mode = State()
    entering_schedule = State()




