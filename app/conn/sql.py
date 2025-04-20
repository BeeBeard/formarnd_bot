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

async_engine = CONN.async_engine


# Добавляем данные к выбранной таблице
async def to_table(table: Dai = None, **kwargs) -> Union[User, bool]:
    if not table or not kwargs:
        return False

    async with async_engine.connect() as session:

        try:
            kwargs["updated"] = datetime.now()
            clear_kwargs = {i: kwargs[i] for i in kwargs if i in table.__table__.columns.keys()}  # type: ignore
            # pprint.pprint(clear_kwargs)
            stmt = insert(table).values(**clear_kwargs)
            # print(stmt.compile(compile_kwargs={"literal_binds": True}))
            stmt = stmt.on_duplicate_key_update(**clear_kwargs)  # вставляем и возвращаем строку
            await session.execute(stmt)
            await session.commit()
            return True

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)
            return False


# noinspection PyTypeChecker
async def get_transaction_by_user(user_id: int, start_period: datetime, end_period: datetime) -> Union[List[Union[Transaction, User]], List]:
    """Транзакции сгруппированные по id и description"""
    async with async_engine.connect() as session:

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
            result = await session.execute(stmt)

            return result.all()

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)
            return []


# noinspection PyTypeChecker
async def get_transaction_info(start_period: datetime, end_period: datetime) -> Union[List[Union[Transaction, User]], List]:
    """Транзакции сгруппированные по id и description"""
    async with async_engine.connect() as session:

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

            result = await session.execute(stmt)

            return result.all()

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)
            return []


async def delete_transaction(uid: Union[int, str]) -> bool:
    """Транзакции сгруппированные по id и description"""
    async with async_engine.connect() as session:

        try:
            stmt = (delete(Transaction).filter(Transaction.uid == int(uid)))
            await session.execute(stmt)
            await session.commit()
            return True

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)
            return False


if __name__ == '__main__':
    pass
