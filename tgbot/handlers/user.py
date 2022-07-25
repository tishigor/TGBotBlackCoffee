from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputFile

from tgbot.config import load_config

from tgbot.keyboards.reply import quantity_equipment, equipment

from tgbot.states.OrderBooking import OrderBooking
# todo импортнуть как в 6 строке
from tgbot.keyboards import kb_yes_no, kb_dates, kb_hours
from tgbot.data_base import sqlite_db
from tgbot.config import load_config



class BOOKING:
    have = False


async def get_str_equipments(ret):
    config = load_config(".env")
    num_boat_dict = {}
    for i, boat in enumerate(config.equipments.equipment):
        num_boat_dict[f'{i}'] = boat
    quantity_dict = {}
    for i, item in enumerate(ret):
        if 0 <= i < 7 and item != '0':
            quantity_dict[f'{num_boat_dict[f"{i}"]}'] = item
    str = ''
    for key in quantity_dict:
        str += f'{key}: {quantity_dict[key]}\n'
    return str

async def user_booking(message: Message):
    read = await sqlite_db.sql_read_for_user(message.from_user.id)
    if read:
        # num_boat_dict = {
        #     '0': 'sup доска',
        #     '1': 'байдарка',
        #     '2': 'каноэ',
        #     '3': 'каяк',
        #     '4': 'мегасап',
        #     '5': 'катамаран',
        #     '6': 'распашная лодка',
        # }
        # quantity_dict = {}
        # for i, item in enumerate(read[0]):
        #     if 0 <= i < 7 and item != '0':
        #         quantity_dict[f'{num_boat_dict[f"{i}"]}'] = item
        # str = ''
        # for key in quantity_dict:
        #     str += f'{key}: {quantity_dict[key]}\n'

        for ret in read:
            str_equipments = await get_str_equipments(ret)
            await message.answer(f'{ret[11]}\n'
                                 f'Дата: {ret[7]}\n'
                                 f'Время: {ret[8]}\n'
                                 f'Оборудование:\n'
                                 f'{str_equipments}',
                                 reply_markup=types.ReplyKeyboardRemove())
            await message.answer('⬆⬆⬆⬆', reply_markup=InlineKeyboardMarkup().
                                 add(InlineKeyboardButton(f'Удалить бронь', callback_data=f'del {ret[9]}')))
    else:
        await message.answer('У вас нет броней!\nСоздать бронь /booking', reply_markup=InlineKeyboardMarkup())


async def del_callback_run_user(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command_from_userid(callback_query.data.replace('del ', ''))
    await callback_query.answer(text='Запись удалена', show_alert=True)


async def user_start(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Помочь забронировать лодку?", reply_markup=kb_yes_no)
    await OrderBooking.waiting_for_start.set()


async def start_value_chosen(message: Message, state: FSMContext):
    # конструкция для получения значений кнопок
    ValueKB_yes_no = []
    for button in kb_yes_no.keyboard:
        ValueKB_yes_no.append(button[0]['text'])
    if message.text.lower() not in ValueKB_yes_no:
        await message.answer('Пожалуйста, выберите "Да" или "Нет", используя клавиатуру ниже.')
        return
    # await state.update_data(user_start=message.text.lower())
    if message.text.lower() == 'да':
        # идем в базу и узнаем есть ли там запись для userid
        read = await sqlite_db.sql_read_for_user(message.from_user.id)
        # если бронь есть спрашиваем о перезаписи
        if read:
            BOOKING.have = True
            await OrderBooking.waiting_for_date.set()
            await message.answer(
                "Вы уже создавали бронь!\nЕсли хотите создать новую, мы перезапишем вашу бронь!\nВы согласны?",
                reply_markup=kb_yes_no)
            return
        await OrderBooking.next()
        await message.answer("Выберите дату:", reply_markup=kb_dates)
    elif message.text.lower() == 'нет':
        await message.reply("Может быть в следующий раз...", reply_markup=types.ReplyKeyboardRemove())
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text="blackcoffee76.ru", url="https://blackcoffee76.ru/"))
        await message.answer("Наш телефон: +74852609002", reply_markup=keyboard)
        await message.answer_location(latitude=57.541343, longitude=40.117726)
        await state.finish()


async def end_of_date(message: Message, state: FSMContext):
    if not BOOKING.have:
        # конструкция для получения значений кнопок
        ValueKB_dates = []
        for button in kb_dates.keyboard:
            ValueKB_dates.append(button[0])
        if message.text not in ValueKB_dates:
            await message.answer("Пожалуйста, выберите дату, используя клавиатуру ниже.")
            return
        await state.update_data(weekday=message.text.split(', ')[0], date=message.text.split(', ')[1])
        await OrderBooking.next()
        await message.answer("Выберите время бронирования", reply_markup=kb_hours)
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
            # сброс псевдоглобальной переменной
            BOOKING.have = False
            await message.answer('Ваша запись успешно удалена!')
            await OrderBooking.waiting_for_date.set()
            await message.answer("Выберите дату:", reply_markup=kb_dates)
        elif message.text.lower() == 'нет':
            await message.answer("Ждем вас по вашей записи!", reply_markup=types.ReplyKeyboardRemove())
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton(text="blackcoffee76.ru", url="https://blackcoffee76.ru/"))
            await message.answer("Наш телефон: +74852609002", reply_markup=keyboard)
            await message.answer_location(latitude=57.541343, longitude=40.117726)
            await message.answer("Просмотерть свои записи /mybooking")
            await state.finish()


async def end_of_hour(message: Message, state: FSMContext):
    # конструкция для получения значений кнопок
    ValueKB_hours = []
    for button in kb_hours.keyboard:
        ValueKB_hours.append(button[0])
    if message.text.lower() not in ValueKB_hours:
        await message.answer("Пожалуйста, выберите время, используя клавиатуру ниже.")
        return
    user_data = await state.get_data()
    kb_equipment = await equipment(user_data['date'])
    await state.update_data(hour=message.text.lower())
    await OrderBooking.next()
    await message.answer(f"Выбери оборудование", reply_markup=kb_equipment)


async def boat_chosen(message: Message, state: FSMContext):
    # if not BOOKING.have:
    # конструкция для получения значений кнопок
    user_data = await state.get_data()
    kb_equipment = await equipment(user_data['date'])
    ValueKB_equipment = []
    for button in kb_equipment.keyboard:
        ValueKB_equipment.append(button[0]['text'])
    if message.text.lower() not in ValueKB_equipment:
        await message.answer("Пожалуйста, выберите оборудование, используя клавиатуру ниже.")
        return
    await state.update_data(boat=message.text.lower())
    # todo не нужно ли это запихнуть в иначе?
    await OrderBooking.next()
    user_data = await state.get_data()
    kb_quantity_equipment = await quantity_equipment(user_data['date'], user_data['hour'], user_data['boat'])
    if not kb_quantity_equipment.keyboard:
        await message.answer("На это время нет доступного оборудования, попробуйте выбрать другое время", reply_markup=kb_hours)
        await OrderBooking.waiting_for_hour.set()
    else:
        await message.answer("Выберите количество оборудования:", reply_markup=kb_quantity_equipment)


async def end_of_booking(message: Message, state: FSMContext):
    # конструкция для получения значений кнопок
    user_data = await state.get_data()
    kb_quantity_equipment = await quantity_equipment(user_data['date'], user_data['hour'], user_data['boat'])
    ValueKB_quantity_equipment = []
    for button in kb_quantity_equipment.keyboard:
        print(button)
        ValueKB_quantity_equipment.append(button[0])
    if message.text.lower() not in ValueKB_quantity_equipment:
        await message.answer("Пожалуйста, выберите количество оборудования, используя клавиатуру ниже.")
        return
    user_data = await state.get_data()
    # todo в одну строку
    if user_data['boat'] == 'sup доска':
        await state.update_data(sap_board=message.text.lower())
    elif user_data['boat'] == 'байдарка':
        await state.update_data(baydarka=message.text.lower())
    elif user_data['boat'] == 'каноэ':
        await state.update_data(canoe=message.text.lower())
    elif user_data['boat'] == 'каяк':
        await state.update_data(kayak=message.text.lower())
    elif user_data['boat'] == 'мега sup':
        await state.update_data(mega_sap_board=message.text.lower())
    elif user_data['boat'] == 'катамаран':
        await state.update_data(catamaran=message.text.lower())
    elif user_data['boat'] == 'распашная лодка':
        await state.update_data(rowing_boat=message.text.lower())
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
        user_data = await state.get_data()
        kb_equipment = await equipment(user_data['date'])
        await message.answer("Выберите оборудование:", reply_markup=kb_equipment)
    elif message.text.lower() == 'нет':

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder='Напишите своё имя')
        keyboard.add(f'Я {message.from_user.first_name}!')

        user_data = await state.get_data()
        await OrderBooking.next()
        # выходим из "да нет"
        await OrderBooking.post_end_booking.set()
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
    await message.reply_sticker(sticker="CAACAgIAAxkBAAEEsD5ieSxEe3mVhao5gEoMb8biHpj-gQAChQIAAladvQqjCXIQX5cmGSQE")
    await message.answer("Спасибо! С Вами свяжутся в ближайшее время.", reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Для просмотра своих броней используйте команду /mybooking")
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
