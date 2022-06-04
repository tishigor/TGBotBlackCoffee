from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# TODO потом убрать !!!
from tgbot.config import load_config

from tgbot.states.OrderBooking import OrderBooking
from tgbot.keyboards import kb_yes_no, kb_equipment, kb_quantity_equipment, kb_dates, kb_hours
from tgbot.data_base import sqlite_db


# TODO потом убрать !!!
config = load_config(".env")


class BOOKING:
    have = False


async def user_booking(message: Message):
    print('qq')
    read = await sqlite_db.sql_read_for_user(message.from_user.id)
    if read:
        for ret in read:
            await message.answer(f'{ret[6]}\n'
                                 f'Дата: {ret[2]}\n'
                                 f'Время: {ret[3]}\n'
                                 f'sup-доски: {ret[1].split("|")[0]}\n'
                                 f'байдарки: {ret[1].split("|")[1]}\n'
                                 f'каноэ: {ret[1].split("|")[2]}\n',
                                 reply_markup=types.ReplyKeyboardRemove())
            await message.answer('⬆⬆⬆⬆', reply_markup=InlineKeyboardMarkup().
                                 add(InlineKeyboardButton(f'Удалить бронь', callback_data=f'del {ret[4]}')))
    else:
        await message.answer('У вас нет броней!\nСоздать бронь /booking', reply_markup=InlineKeyboardMarkup())


async def del_callback_run_user(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command_from_userid(callback_query.data.replace('del ', ''))
    await callback_query.answer(text='Запись удалена', show_alert=True)


async def user_start(message: Message):
    await message.answer("Помочь забронировать лодку?",
                         reply_markup=kb_yes_no)
    await OrderBooking.waiting_for_start.set()


async def start_value_chosen(message: Message, state: FSMContext):
    # конструкция для получения значений кнопок
    ValueKB_yes_no = []
    for button in kb_yes_no.keyboard:
        ValueKB_yes_no.append(button[0]['text'])
    if message.text.lower() not in ValueKB_yes_no:
        await message.answer('Пожалуйста, выберите "Да" или "Нет", используя клавиатуру ниже.')
        return
    await state.update_data(user_start=message.text.lower())
    if message.text.lower() == 'да':
        # идем в базу и узнаем есть ли там запись для userid
        read = await sqlite_db.sql_read_for_user(message.from_user.id)
        print('read', read)
        # если бронь есть спрашиваем о перезаписи
        if read:
            BOOKING.have = True
            await OrderBooking.waiting_for_boat_name.set()
            await message.answer(
                "Вы уже создавали бронь!\nЕсли хотите создать новую, мы перезапишем вашу бронь!\nВы согласны?",
                reply_markup=kb_yes_no)
            return
        print('BOOKING.have', BOOKING.have)
        print('я всетаки зашел сюда')
        await OrderBooking.next()
        await message.answer("Выберите оборудование:", reply_markup=kb_equipment)
    elif message.text.lower() == 'нет':
        await message.reply("Может быть в следующий раз...", reply_markup=types.ReplyKeyboardRemove())
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text="blackcoffee76.ru", url="https://blackcoffee76.ru/"))
        await message.answer("Наш телефон: +74852609002", reply_markup=keyboard)
        await message.answer_location(latitude=57.541343, longitude=40.117726)
        await state.finish()


async def boat_chosen(message: Message, state: FSMContext):
    if not BOOKING.have:
        # конструкция для получения значений кнопок
        ValueKB_equipment = []
        for button in kb_equipment.keyboard:
            ValueKB_equipment.append(button[0]['text'])
        if message.text.lower() not in ValueKB_equipment:
            await message.answer("Пожалуйста, выберите оборудование, используя клавиатуру ниже.")
            return
        await state.update_data(boat=message.text.lower())
        await OrderBooking.next()
        # тут вызываю функцию и отдаю в нее НАЗВАНИЕ ЛОДКИ и ДАТУ и ВРЕМЯ. Функция вернет клавиатуру с кол-вом оборудования
        await message.answer("Выберите количество оборудования:", reply_markup=kb_quantity_equipment)
    elif BOOKING.have:
        # конструкция для получения значений кнопок
        ValueKB_yes_no = []
        for button in kb_yes_no.keyboard:
            ValueKB_yes_no.append(button[0]['text'])
        if message.text.lower() not in ValueKB_yes_no:
            await message.answer('Пожалуйста, выберите "Да" или "Нет", используя клавиатуру ниже.')
            return
        if message.text.lower() == 'да':
            await sqlite_db.sql_delete_command_for_user(message.from_user.id)
            # сброс глобальной переменной
            BOOKING.have = False
            await message.answer('Ваша запись успешно удалена!')
            await OrderBooking.waiting_for_boat_name.set()
            await message.answer("Выберите оборудование:", reply_markup=kb_equipment)
        elif message.text.lower() == 'нет':
            await message.answer("Ждем вас по вашей записи!", reply_markup=types.ReplyKeyboardRemove())
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton(text="blackcoffee76.ru", url="https://blackcoffee76.ru/"))
            await message.answer("Наш телефон: +74852609002", reply_markup=keyboard)
            await message.answer_location(latitude=57.541343, longitude=40.117726)
            await message.answer("Просмотерть свои записи /mybooking")
            await state.finish()


async def end_of_booking(message: Message, state: FSMContext):
    # конструкция для получения значений кнопок
    ValueKB_quantity_equipment = []
    for button in kb_quantity_equipment.keyboard:
        print(button)
        ValueKB_quantity_equipment.append(button[0])
    print('ValueKB_quantity_equipment', ValueKB_quantity_equipment)
    if message.text.lower() not in ValueKB_quantity_equipment:
        await message.answer("Пожалуйста, выберите количество оборудования, используя клавиатуру ниже.")
        return
    user_data = await state.get_data()
    # для вноса инфы о всех лодках и количествах
    try:
        if user_data['boats']:
            boats_list = user_data['boats'].split('|')
        else:
            boats_list = ['0', '0', '0']
            print('есть')
    except:
        boats_list = ['0', '0', '0']
    if user_data['boat'] == 'sup-доска':
        boats_list[0] = message.text.lower()
    elif user_data['boat'] == 'байдарка':
        boats_list[1] = message.text.lower()
    elif user_data['boat'] == 'каноэ':
        boats_list[2] = message.text.lower()
    boats = '|'.join(boats_list)
    print('boats', boats)
    await state.update_data(quantity=message.text.lower())
    await state.update_data(boats=boats)
    user_data = await state.get_data()
    print(user_data['boats'])

    # Для последовательных шагов можно не указывать название состояния, обходясь next()
    await OrderBooking.next()
    await message.answer("Желаете забронировать что-нибудь еще?", reply_markup=kb_yes_no)


async def anything_else(message: Message, state: FSMContext):
    # конструкция для получения значений кнопок
    ValueKB_yes_no = []
    for button in kb_yes_no.keyboard:
        ValueKB_yes_no.append(button[0]['text'])
    if message.text.lower() not in ValueKB_yes_no:
        await message.answer('Пожалуйста, выберите "Да" или "Нет", используя клавиатуру ниже.')
        return
    if message.text.lower() == 'да':
        # идем повторно по выбору оборудования
        await OrderBooking.waiting_for_boat_name.set()
        await message.answer("Выберите оборудование:", reply_markup=kb_equipment)
    elif message.text.lower() == 'нет':
        # выходим из "да нет"
        await OrderBooking.waiting_for_date.set()
        await message.answer("Выберите дату бронирования", reply_markup=kb_dates)


async def end_of_date(message: Message, state: FSMContext):
    # конструкция для получения значений кнопок
    ValueKB_dates = []
    for button in kb_dates.keyboard:
        ValueKB_dates.append(button[0])
    if message.text not in ValueKB_dates:
        await message.answer("Пожалуйста, выберите дату, используя клавиатуру ниже.")
        return
    await state.update_data(date=message.text.lower())
    await OrderBooking.next()
    await message.answer("Выберите время бронирования", reply_markup=kb_hours)


async def end_of_hour(message: Message, state: FSMContext):
    # конструкция для получения значений кнопок
    ValueKB_hours = []
    for button in kb_hours.keyboard:
        ValueKB_hours.append(button[0])
    if message.text.lower() not in ValueKB_hours:
        await message.answer("Пожалуйста, выберите время, используя клавиатуру ниже.")
        return
    await state.update_data(hour=message.text.lower())
    user_data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder='Напишите своё имя')
    keyboard.add(f'Я {message.from_user.first_name}!')
    await OrderBooking.next()
    await message.answer(f"Ваша бронь\n"
                         f"Дата: {user_data['date']}\n"
                         f"Время: {user_data['hour']}\n"
                         f"sup-доски: {user_data['boats'].split('|')[0]}\n"
                         f"байдарки: {user_data['boats'].split('|')[1]}\n"
                         f"каноэ: {user_data['boats'].split('|')[2]}\n"
                         )
    await message.answer(f"К вам можно обращаться как к {message.from_user.first_name}?\nИли введите своё имя сами",
                         reply_markup=keyboard)


async def get_user_name(message: Message, state: FSMContext):
    if len(message.text) > 30:
        await message.answer("Ваше имя слишком длинное! Попытайтесь уложиться в 30 символов.")
        return
    if message.text == f'Я {message.from_user.first_name}!':
        first_name = message.from_user.first_name
    else:
        first_name = message.text
    await state.update_data(userid=message.from_user.id)
    await state.update_data(username=message.from_user.username)
    await state.update_data(first_name=first_name)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Поделиться номером", request_contact=True))
    await OrderBooking.next()
    await message.answer("Поделитесь номером, нажав на кнопку, для связи с нами⬇⬇⬇", reply_markup=keyboard)


async def get_user_phone(message: types.Contact, state: FSMContext):
    await state.update_data(userphone=message.contact["phone_number"])
    user_data = await state.get_data()
    print('user_data', user_data)
    await Bot(token=config.tg_bot.token, parse_mode='HTML').send_sticker(chat_id=message.from_user.id,
                           sticker="CAACAgIAAxkBAAEEsD5ieSxEe3mVhao5gEoMb8biHpj-gQAChQIAAladvQqjCXIQX5cmGSQE")
    await message.answer("Спасибо! С Вами свяжутся в ближайшее время.", reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Для просмотра своих броней используйте команду /mybooking")

    for admin in load_config(".env").tg_bot.admin_ids:
        await Bot(token=load_config(".env").tg_bot.token, parse_mode='HTML').send_message(admin,
                                                                                          f'{user_data["first_name"]} зарегистрировался!\n'
                                                                                          f'Юзернейм: @{user_data["username"]}\n'
                                                                                          f'Телефон: {user_data["userphone"]}\n'
                                                                                          f'sup-доски: {user_data["boats"].split("|")[0]}\n'
                                                                                          f'байдарки: {user_data["boats"].split("|")[1]}\n'
                                                                                          f'каноэ: {user_data["boats"].split("|")[2]}\n'
                                                                                          f'Дата: {user_data["date"]}\n'
                                                                                          f'Время: {user_data["hour"]}\n')
    await sqlite_db.sql_add_command(state)
    await state.finish()


# Значение состояния "*" при регистрации food_start() означает срабатывание при любом состоянии
def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["booking"], state="*")
    dp.register_message_handler(user_booking, commands=["mybooking"], state="*")
    dp.register_callback_query_handler(del_callback_run_user, lambda x: x.data and x.data.startswith('del '))
    dp.register_message_handler(start_value_chosen, state=OrderBooking.waiting_for_start)
    dp.register_message_handler(boat_chosen, state=OrderBooking.waiting_for_boat_name)
    dp.register_message_handler(end_of_booking, state=OrderBooking.waiting_for_quantity)
    dp.register_message_handler(anything_else, state=OrderBooking.waiting_for_anything_else)
    dp.register_message_handler(end_of_date, state=OrderBooking.waiting_for_date)
    dp.register_message_handler(end_of_hour, state=OrderBooking.waiting_for_hour)
    dp.register_message_handler(get_user_name, state=OrderBooking.post_end_booking)
    dp.register_message_handler(get_user_phone, content_types=['contact'], state=OrderBooking.waiting_for_name)
