# Модель подключения к базе данных

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class ConData:

    def __init__(self):

        self.engine = create_engine('sqlite:///FormRND_bot.db')
        self.session = sessionmaker(self.engine)


CONN = ConData()


if __name__ == '__main__':
    pass
