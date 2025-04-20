from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from app.bot.middleware import TForm
from app.bot.routers import r_final


logger.info(f"Инициируем диспетчер")

DP = Dispatcher(storage=MemoryStorage())    # Инициируем диспетчер
DP.callback_query.middleware.register(TForm())

# Список подключаемых роутеров
routers = [
    r_final.r_any
]


for i, value in enumerate(routers):
    logger.info(f'Подключил {i+1} роутер: {value.name}')


DP.include_routers(*routers)    # Подключаем роутеры

if __name__ == "__main__":
    pass
