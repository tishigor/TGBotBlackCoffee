import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.common import register_common
from tgbot.handlers.echo import register_echo
from tgbot.handlers.user import register_user
# from tgbot.middlewares.db import DbMiddleware
from tgbot.utils.set_bot_commands import set_default_commands
from tgbot.data_base import sqlite_db

# from create_bot import dp, bot

logger = logging.getLogger(__name__)


# def register_all_middlewares(dp):
#     dp.setup_middleware(DbMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_common(dp)
    register_user(dp)
    register_echo(dp)




async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    # старт бд
    sqlite_db.sql_start()

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    # register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    # from utils.notify_admins import on_startup_notify
    # await on_startup_notify(dp)
    await set_default_commands(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
