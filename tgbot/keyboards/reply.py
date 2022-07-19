from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import datetime


# --------------------------------------клавиатура "да нет"------------------------------------------------
from tgbot.data_base import sqlite_db

byes = KeyboardButton('да')
bno = KeyboardButton('нет')
# замена клавы обычной на клаву созданную
kb_yes_no = ReplyKeyboardMarkup(resize_keyboard=True)
# метод insert для добавления кнопки в один ряд с предыдущей
# метод row для добавления всех кнопок в одну строку
kb_yes_no.add(byes).add(bno)
# ---------------------------------------------------------------------------------------------------------

# --------------------------------------клавиатура с оборудованием-----------------------------------------
bsup = KeyboardButton('sup-доска')
bbaydarka = KeyboardButton('байдарка')
bkanoe = KeyboardButton('каноэ')
kb_equipment = ReplyKeyboardMarkup(resize_keyboard=True)
kb_equipment.add(bsup).add(bbaydarka).add(bkanoe)
# ---------------------------------------------------------------------------------------------------------

# --------------------------------------клавиатура с кол-вом оборудования----------------------------------
async def quantity_equipment(date, hour, boat):
    # расчет свободного кол-ва оборудования на час будет происходить в программе
    # когда пользователь выбирает дату и время брони прога делает запрос в котором чекает оборудование на час и возвращает число
    # todo для этого бот сначала спрашивает про дату, а потом уже про кол-во


    # todo если пустой запрос то соунт = 0)
    read = await sqlite_db.sql_read_for_time(date, hour)
    print('read', read)
    count = 0
    for ret in read:
        if boat == 'sup-доска':
            count = int(ret[1].split('|')[0])
        elif boat == 'байдарка':
            count = int(ret[1].split('|')[1])
        elif boat == 'каноэ':
            count = int(ret[1].split('|')[2])

    # уменьшаемое - переменная значение которой надо записать где-то не тут
    quantity = 10 - count
    available_quantity = [str(i) for i in range(1, quantity + 1)]

    kb_quantity_equipment = ReplyKeyboardMarkup(resize_keyboard=True)
    for value in available_quantity:
        kb_quantity_equipment.add(value)
    return kb_quantity_equipment
# ---------------------------------------------------------------------------------------------------------

# --------------------------------------клавиатура с датами------------------------------------------------
months = {1: 'января', 2: 'ферваля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
          9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}
global date_for_buttons
date_for_buttons = []
kb_dates = ReplyKeyboardMarkup(resize_keyboard=True)
for day in range(1, 7):
    # дата через i
    future_date = datetime.datetime.today() + datetime.timedelta(days=day)
    date_for_buttons.append(str(future_date.day) + " " + months[future_date.month])
    kb_dates.add(str(future_date.day) + " " + months[future_date.month])
# ---------------------------------------------------------------------------------------------------------

# --------------------------------------клавиатура с часами------------------------------------------------
hours = ['14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']
kb_hours = ReplyKeyboardMarkup(resize_keyboard=True)
for value in hours:
    kb_hours.add(value)
# ---------------------------------------------------------------------------------------------------------

