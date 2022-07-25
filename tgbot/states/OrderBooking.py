from aiogram.dispatcher.filters.state import StatesGroup, State


class OrderBooking(StatesGroup):
    waiting_for_start = State()
    waiting_for_date = State()
    waiting_for_hour = State()
    waiting_for_boat_name = State()
    waiting_for_quantity = State()
    waiting_for_anything_else = State()
    post_end_booking = State()
    waiting_for_name = State()
