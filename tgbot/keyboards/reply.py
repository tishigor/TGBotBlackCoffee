from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import datetime


# --------------------------------------клавиатура "да нет"------------------------------------------------
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
available_quantity = ["1", "2", "3", "4", '5', "6", "7", "8", "9", "10"]

kb_quantity_equipment = ReplyKeyboardMarkup(resize_keyboard=True)
for value in available_quantity:
    kb_quantity_equipment.add(value)
# ---------------------------------------------------------------------------------------------------------

# --------------------------------------клавиатура с датами------------------------------------------------
months = {1: 'Января', 2: 'Ферваля', 3: 'Марта', 4: 'Апреля', 5: 'Мая', 6: 'Июня', 7: 'Июля', 8: 'Августа',
          9: 'Сентября', 10: 'Октября', 11: 'Ноября', 12: 'Декабря'}
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

