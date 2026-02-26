"""FSM states for TaskMaster Bot."""
from aiogram.fsm.state import State, StatesGroup


class AddTaskStates(StatesGroup):
    waiting_title = State()
