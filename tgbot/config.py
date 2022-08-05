from dataclasses import dataclass

from environs import Env


# for Python version < 3.9
# from typing import List


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]  # for Python version >= 3.9
    # admin_ids: list # for Python version < 3.9 write "List(int)"
    # use_redis: bool


@dataclass
class EquipmentsConfig:
    equipment: dict
    equipment_db: list[str]
    quantity_for_user: list[int]


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    equipments: EquipmentsConfig


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            # use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        ),
        equipments=EquipmentsConfig(
            equipment=dict(zip(env.list("EQUIPMENTS"), env.list("QUANTITY"))),
            equipment_db=list(map(str, env.list("EQUIPMENTS_DB"))),
            quantity_for_user=dict(zip(env.list("EQUIPMENTS"), env.list("QUANTITY_FOR_BOOKING"))),
        ),
    )
