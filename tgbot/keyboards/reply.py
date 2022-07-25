from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import datetime

from tgbot.config import load_config
from tgbot.data_base import sqlite_db


# --------------------------------------клавиатура "да нет"------------------------------------------------
byes = KeyboardButton('да')
bno = KeyboardButton('нет')
kb_yes_no = ReplyKeyboardMarkup(resize_keyboard=True)
kb_yes_no.add(byes).add(bno)
# ---------------------------------------------------------------------------------------------------------

# --------------------------------------клавиатура с оборудованием-----------------------------------------
async def equipment(date):
    if date.split(',')[0] == 'суббота' or date.split(',')[0] == 'воскресенье':
        baydarka = KeyboardButton('байдарка')
        canoe = KeyboardButton('каноэ')
        kayak = KeyboardButton('каяк')
        mega_sap_board = KeyboardButton('мега sup')
        catamaran = KeyboardButton('катамаран')
        rowing_boat = KeyboardButton('распашная лодка')
        kb_equipment = ReplyKeyboardMarkup(resize_keyboard=True)
        kb_equipment.add(baydarka).add(canoe).add(kayak).add(mega_sap_board).add(catamaran).add(rowing_boat)
    else:
        sap_board = KeyboardButton('sup доска')
        baydarka = KeyboardButton('байдарка')
        canoe = KeyboardButton('каноэ')
        kayak = KeyboardButton('каяк')
        mega_sap_board = KeyboardButton('мега sup')
        catamaran = KeyboardButton('катамаран')
        rowing_boat = KeyboardButton('распашная лодка')
        kb_equipment = ReplyKeyboardMarkup(resize_keyboard=True)
        kb_equipment.add(sap_board).add(baydarka).add(canoe).add(kayak).add(mega_sap_board).add(catamaran).add(rowing_boat)
    return kb_equipment
# ---------------------------------------------------------------------------------------------------------

# --------------------------------------клавиатура с кол-вом оборудования----------------------------------
async def quantity_equipment(date, hour, boat):
    config = load_config(".env")
    # todo если пустой запрос то count = 0)
    read = await sqlite_db.sql_read_for_time(date, hour)
    list_equipments = list(config.equipments.equipment.keys())
    quantity = int(config.equipments.equipment[boat])
    count = 0
    for ret in read:
        # if boat == 'sup доска':
        list_equipments.index(boat)
        count += int(ret[list_equipments.index(boat)])
        # elif boat == 'байдарка':
        #     count = int(ret[1].split('|')[1])
        # elif boat == 'каноэ':
        #     count = int(ret[1].split('|')[2])
    # уменьшаемое - переменная значение которой надо записать где-то не тут
    quantity = quantity - count
    available_quantity = [str(i) for i in range(1, quantity + 1)]

    kb_quantity_equipment = ReplyKeyboardMarkup(resize_keyboard=True)
    for value in available_quantity:
        kb_quantity_equipment.add(value)
    return kb_quantity_equipment
# ---------------------------------------------------------------------------------------------------------

# --------------------------------------клавиатура с датами------------------------------------------------
months = {1: 'января', 2: 'ферваля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
          9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}
dict_weekday = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
# todo зачем глобальная переменная?
# global date_for_buttons
# date_for_buttons = []
kb_dates = ReplyKeyboardMarkup(resize_keyboard=True)
for day in range(1, 7):
    # дата через i
    future_date = datetime.datetime.today() + datetime.timedelta(days=day)
    # date_for_buttons.append(dict_weekday[future_date.weekday()] + ", " + str(future_date.day) + " " + months[future_date.month])
    kb_dates.add(dict_weekday[future_date.weekday()] + ", " + str(future_date.day) + " " + months[future_date.month])
# ---------------------------------------------------------------------------------------------------------

# --------------------------------------клавиатура с часами------------------------------------------------
hours = ['14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']
kb_hours = ReplyKeyboardMarkup(resize_keyboard=True)
for value in hours:
    kb_hours.add(value)
# ---------------------------------------------------------------------------------------------------------

