# Модель подключения к базе данных

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.config import CONFIG


class ConData:

    def __init__(self):

        self.engine = create_engine('sqlite:///FormRND_bot.db')
        self.session = sessionmaker(self.engine)


CONN = ConData()


if __name__ == '__main__':
    pass
