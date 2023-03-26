from aiogram.dispatcher.filters.state import State, StatesGroup


class UsersStates(StatesGroup):
    wait_response = State()
