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
from tgbot.utils.notify_admins import on_startup_notify
# from tgbot.middlewares.db import DbMiddleware
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.utils.set_bot_commands import set_default_commands
from tgbot.data_base import sqlite_db

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    # dp.setup_middleware(DbMiddleware())
    dp.setup_middleware(EnvironmentMiddleware(config=config))

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

    await on_startup_notify(dp)
    await set_default_commands(dp)

    # start
    try:
        # пропускаем все накопленные входящие
        await bot.delete_webhook(drop_pending_updates=True)
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
