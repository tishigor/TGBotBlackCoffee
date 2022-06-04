from aiogram import Dispatcher, types, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.data_base import sqlite_db



async def admin_start(message: Message):
    await message.reply("Hello, admin!\n"
                        "Use /bookings", reply_markup=types.ReplyKeyboardRemove())


async def admin_booking(message: Message):
    print('qq')
    read = await sqlite_db.sql_read_all_for_admin()
    if read:
        for ret in read:
            await message.answer(f'{ret[6]}\n'
                                 f'Юзернейм: @{ret[5]}\n'
                                 f'Телефон: {ret[7]}\n'
                                 f'Дата: {ret[2]}\n'
                                 f'Время: {ret[3]}\n'
                                 f'sup-доски: {ret[1].split("|")[0]}\n'
                                 f'байдарки: {ret[1].split("|")[1]}\n'
                                 f'каноэ: {ret[1].split("|")[2]}\n'
                                 )
            await message.answer('⬆⬆⬆⬆', reply_markup=InlineKeyboardMarkup().
                                 add(InlineKeyboardButton(f'Удалить бронь пользователя {ret[6]}', callback_data=f'del {ret[4]}')))
    else:
        await message.answer('Броней нет', reply_markup=InlineKeyboardMarkup())


async def del_callback_run_admin(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command_from_userid(callback_query.data.replace('del ', ''))
    await callback_query.answer(text='Запись удалена', show_alert=True)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_message_handler(admin_booking, commands=["bookings"], state="*", is_admin=True)
    dp.register_callback_query_handler(del_callback_run_admin, lambda x: x.data and x.data.startswith('del '), is_admin=True)
    # dp.callback_query_handler(del_callback_run, Text(startswith='del '), is_admin=True)

