# Модуль с запросами к базе данных

from datetime import datetime
from typing import Union, List

from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept as Dai

from app.conn import CONN
from app.conn.tables import Transaction, User

async_engine = CONN.engine


# Добавляем данные к выбранной таблице
def to_table(table: Dai = None, **kwargs) -> Union[User, bool]:
    if not table or not kwargs:
        return False

    with async_engine.connect() as session:

        try:
            kwargs["updated"] = datetime.now()
            clear_kwargs = {i: kwargs[i] for i in kwargs if i in table.__table__.columns.keys()}  # type: ignore
            # pprint.pprint(clear_kwargs)
            stmt = insert(table).values(**clear_kwargs).prefix_with('OR REPLACE')
            # print(stmt.compile(compile_kwargs={"literal_binds": True}))
            # stmt = stmt.on_duplicate_key_update(**clear_kwargs)  # вставляем и возвращаем строку
            session.execute(stmt)
            session.commit()
            return True

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(e)
            return False


# noinspection PyTypeChecker
def get_transaction_by_user(user_id: int, start_period: datetime, end_period: datetime) -> Union[List[Union[Transaction, User]], List]:
    """Транзакции сгруппированные по id и description"""
    with async_engine.connect() as session:

        try:
            stmt = (
                select(
                    Transaction,
                    User.username
                )
                .join(User, Transaction.id == User.id)
                .filter(
                    Transaction.updated >= start_period,
                    Transaction.updated < end_period,
                    Transaction.id == user_id,
                )
                .order_by(Transaction.uid)
            )
            result = session.execute(stmt)

            return result.all()

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(e)
            return []


# noinspection PyTypeChecker
def get_transaction_info(start_period: datetime, end_period: datetime) -> Union[List[Union[Transaction, User]], List]:
    """Транзакции сгруппированные по id и description"""
    with async_engine.connect() as session:

        try:
            stmt = (
                select(
                    Transaction,
                    User.username
                )
                .join(User, Transaction.id == User.id)
                .filter(
                    Transaction.updated >= start_period,
                    Transaction.updated < end_period,
                )
                .order_by(Transaction.uid)

            )

            result = session.execute(stmt)

            return result.all()

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(e)
            return []


def delete_transaction(uid: Union[int, str]) -> bool:
    """Транзакции сгруппированные по id и description"""
    with async_engine.connect() as session:

        try:
            stmt = (delete(Transaction).filter(Transaction.uid == int(uid)))
            session.execute(stmt)
            session.commit()
            return True

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(e)
            return False


if __name__ == '__main__':
    pass
