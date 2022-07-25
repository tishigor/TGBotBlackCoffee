from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("booking", "Забронировать оборудование"),
        types.BotCommand("mybooking", "Моя бронь"),
        types.BotCommand("cancel", "Отменить текущее действие"),
        types.BotCommand("help", "Помощь"),
    ])
