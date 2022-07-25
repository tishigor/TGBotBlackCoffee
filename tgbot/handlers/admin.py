from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.config import load_config
from tgbot.data_base import sqlite_db

from tgbot.handlers.user import get_str_equipments
from tgbot.keyboards import kb_dates, kb_hours

import xlwt



async def admin_start(message: Message, state: FSMContext):
    await state.finish()
    await message.reply("Привет, админ!\n"
                        "/bookings- просмотр броней\n"
                        "/report- создание отчета", reply_markup=types.ReplyKeyboardRemove())


async def admin_booking(message: Message):
    read = await sqlite_db.sql_read_all_for_admin()
    if read:
        for ret in read:
            str_equipments = await get_str_equipments(ret)
            await message.answer(f'{ret[11]}\n'
                                 f'Юзернейм: @{ret[10]}\n'
                                 f'Телефон: {ret[12]}\n'
                                 f'Дата: {ret[8]}\n'
                                 f'Время: {ret[9]}\n'
                                 f'Оборудование:\n'
                                 f'{str_equipments}'
                                 )
            await message.answer('⬆⬆⬆⬆', reply_markup=InlineKeyboardMarkup().
                                 add(InlineKeyboardButton(f'Удалить бронь пользователя {ret[11]}', callback_data=f'del {ret[9]}')))
    else:
        await message.answer('Броней нет', reply_markup=InlineKeyboardMarkup())


async def del_callback_run_admin(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command_from_userid(callback_query.data.replace('del ', ''))
    await callback_query.answer(text='Запись удалена', show_alert=True)


async def creating_report(message: Message):
    config = load_config(".env")

    font0 = xlwt.Font()
    font0.name = 'Times New Roman'
    font0.colour_index = 2
    font0.bold = True

    style0 = xlwt.XFStyle()
    style0.font = font0

    wb = xlwt.Workbook()

    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 251, 228, 228)

    ws = wb.add_sheet('Sheet 1')

    borders = xlwt.Borders()  # Pattern Borders

    # borders.right = borders.NO_LINE  # По умолчанию границы нет, NO_LINE
    # borders.top = borders.THIN   # Тонкая граница
    # borders.bottom = borders.MEDIUM  # Пунктирная граница
    # borders.left = borders.THICK  # Толстая граница

    borders.right = borders.THIN
    borders.top = borders.THIN
    borders.bottom = borders.THIN
    borders.left = borders.THIN

    # borders.left_colour = 0x90  # Раскраска границы
    # borders.right_colour = 0x90
    # borders.top_colour = 0x90
    # borders.bottom_colour = 0x90

    style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour')
    style1 = xlwt.easyxf()
    style.borders = style1.borders = borders

    ws.write_merge(0, 1, 0, 0, 'ID', style1)
    ws.write_merge(0, 1, 1, 1, 'Имя', style1)
    ws.write_merge(0, 1, 2, 2, 'Телефон', style1)
    ws.write_merge(0, 1, 3, 3, 'Оборудование', style1)

    num_hours = len(kb_hours['keyboard'])

    # с 4 ячейки начинаем заполнение ячеек с датами
    first_date_cell = first_date_cell_for_dict = 4
    first_hour_cell_for_dict = 0
    # дикт- Дата: 'номер ячейки в отчете'
    dict_date_cells = {}
    for date in kb_dates['keyboard']:
        dict_date_cells[f'{date[0]}'] = first_date_cell_for_dict
        first_date_cell_for_dict += 8

    # дикт- Час: 'номер ячейки в отчете'
    dict_hour_cells = {}
    for hour in kb_hours['keyboard']:
        dict_hour_cells[f'{hour[0]}'] = first_hour_cell_for_dict
        first_hour_cell_for_dict += 1

    for date in kb_dates['keyboard']:
        ws.write_merge(0, 0, first_date_cell, first_date_cell + num_hours - 1, date, style1)
        # first_date_cell += num_hours
        for hour in kb_hours['keyboard']:
            ws.col(first_date_cell).width = 1400
            ws.write(1, first_date_cell, hour, style1)
            first_date_cell += 1
    # todo разделить дату на день недели и день месяца чтобы сортировка норм проходила по дате для отчета
    read = await sqlite_db.sql_read_all_for_report(list(dict_date_cells)[0].split(', ')[1])
    if read:
        first_equipment_cell = 2
        for ret in read:
            ws.write(first_equipment_cell, 0, ret[9], style1)
            ws.write(first_equipment_cell, 1, ret[11], style1)
            ws.write(first_equipment_cell, 2, ret[12], style1)
            list_equipments = list(config.equipments.equipment.keys())
            for equipment in list_equipments:
                ws.write(first_equipment_cell, 3, equipment, style1)
                ws.write(first_equipment_cell, dict_date_cells[ret[13] + ', ' + ret[7]] + dict_hour_cells[ret[8]],
                         ret[list_equipments.index(equipment)], style)
                first_equipment_cell += 1
    else:
        await message.answer('Броней нет', reply_markup=InlineKeyboardMarkup())
    ws.col(0).width = 3000
    ws.col(2).width = 4000
    ws.col(3).width = 4000
    wb.save('report.xls')
    file = open('report.xls', 'rb')
    await message.reply_document(file)
    file.close()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_message_handler(admin_booking, commands=["bookings"], state="*", is_admin=True)
    dp.register_message_handler(creating_report, commands=["report"], state="*", is_admin=True)
    dp.register_callback_query_handler(del_callback_run_admin, lambda x: x.data and x.data.startswith('del '), is_admin=True)
    # dp.callback_query_handler(del_callback_run, Text(startswith='del '), is_admin=True)

