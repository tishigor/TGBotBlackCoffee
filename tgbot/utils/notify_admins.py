import logging

from aiogram import Dispatcher

# from tgbot import config
# import bot
from tgbot.config import load_config



async def on_startup_notify(dp: Dispatcher):
    print("Бот запущен")
    config = load_config(".env")
    for admin in config.tg_bot.admin_ids:
        try:
            await dp.bot.send_message(admin, "Бот запущен", disable_notification=True)
        except Exception as err:
            logging.exception(err)
