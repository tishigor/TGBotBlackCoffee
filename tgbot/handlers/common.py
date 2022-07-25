from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Привет, я чат бот для бронирования оборудования!"
        "\nЗабронировать оборудование: /booking"
        "\nПосмотреть свои записи: /mybooking",
        reply_markup=types.ReplyKeyboardRemove()
    )


async def bot_help(message: types.Message):
    text = [
        'Список команд: ',
        '/start - Начать диалог',
        '/booking - Забронировать оборудование',
        '/mybooking - Посмотреть свои записи',
        '/cancel - Отменить текущее действие'
    ]
    await message.answer('\n'.join(text))


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())


def register_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(bot_help, commands="help", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
