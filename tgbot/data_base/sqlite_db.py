import sqlite3 as sq
# from create_bot import bot
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot.config import load_config

# todo для нормально работы создать файл create_bot.py в котором будет создаваться экземпляр бота. Далее просто импортим файл в файл запуска
config = load_config(".env")
storage = MemoryStorage()
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)


def sql_start():
    global base, cur
    base = sq.connect('booking_black_coffee.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    # PRIMARY KEY к userid
    base.execute('CREATE TABLE IF NOT EXISTS '
                 'bookings(start_booking TEXT, boats TEXT, date TEXT,'
                 ' hour TEXT, userid INT PRIMARY KEY, username TEXT, first_name TEXT, userphone TEXT)')
    base.commit()


async def sql_add_command(state):
    # асинхронно запускаем менеджер контекста with
    # state.proxy() as data - открываем словарь
    async with state.proxy() as data:
        list_values = [
            data['user_start'],
            data['boats'],
            data['date'],
            data['hour'],
            data['userid'],
            data['username'],
            data['first_name'],
            data['userphone'],
        ]
        # синтаксис sqlite требует перевод значений в кортеж
        cur.execute('INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?, ?, ?)', tuple(list_values))
        base.commit()


async def sql_read_delete_admin(message):
    for ret in cur.execute('SELECT * FROM bookings').fetchall():
        await bot.send_message(message.from_user.id, f'{ret[6]}\n'
                                                     f'Юзернейм {ret[5]}\n'
                                                     f'Телефон {ret[7]}\n'
                                                     f'Дата: {ret[2]}\n'
                                                     f'Время: {ret[3]}\n'
                                                     f'sup-доски: {ret[1].split("|")[0]}\n'
                                                     f'байдарки: {ret[1].split("|")[1]}\n'
                                                     f'каноэ: {ret[1].split("|")[2]}\n'
                               )


async def sql_read_all_for_admin():
    return cur.execute('SELECT * FROM bookings ORDER BY date').fetchall()


async def sql_read_all_for_report(first_date):
    return cur.execute('SELECT * FROM bookings WHERE date >= ? ORDER BY date', (first_date, )).fetchall()


async def sql_read_for_user(userid):
    return cur.execute('SELECT * FROM bookings WHERE userid == ?', (userid,)).fetchall()


async def sql_read_for_time(date, hour):
    return cur.execute('SELECT * FROM bookings WHERE date == ? AND hour == ?', (date, hour)).fetchall()


# удаление записи по userid
async def sql_delete_command_from_userid(data):
    cur.execute('DELETE FROM bookings WHERE userid == ?', (data,))
    base.commit()


async def sql_delete_command_for_user(userid):
    cur.execute('DELETE FROM bookings WHERE userid == ?', (userid,))
    base.commit()
