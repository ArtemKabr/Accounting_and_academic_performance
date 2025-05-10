from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    choosing_role = State()
    waiting_for_password_parent = State()
    waiting_for_fio_parent = State()
    waiting_for_password_teacher = State()