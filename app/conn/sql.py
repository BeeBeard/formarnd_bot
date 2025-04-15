# Модуль с запросами к базе данных

from datetime import datetime
from typing import Union, List
from loguru import logger
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept as Dai

from app.conn import CONN
from app.conn import tables
from sqlalchemy import func


async_engine = CONN.async_engine


# Добавляем данные к выбранной таблице
async def to_table(table: Dai = None, **kwargs) -> Union[tables.User, bool]:
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


async def get_user(user_id: int) -> Union[tables.User, bool]:
    if not user_id:
        return False

    async with async_engine.connect() as session:

        try:
            stmt = (select(tables.User).filter(tables.User.id == user_id))
            result = await session.execute(stmt)

            return result.all()

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)
            return False


async def get_group_transaction_info(start_period: datetime, end_period: datetime) -> Union[List[Union[tables.Transaction, tables.User]], List]:
    """Транзакции сгруппированные по id и description"""
    async with async_engine.connect() as session:

        try:
            stmt = (
                select(
                    tables.Transaction.id,
                    tables.Transaction.description,
                    tables.User.username,
                    func.sum(tables.Transaction.number).label("number")
                )
                .join(tables.User, tables.Transaction.id == tables.User.id)
                .filter(
                    tables.Transaction.updated >= start_period,
                    tables.Transaction.updated < end_period,
                )
                .group_by(tables.Transaction.id, tables.User.username, tables.Transaction.description)
                .order_by(tables.Transaction.id, tables.User.username, tables.Transaction.description)
            )

            result = await session.execute(stmt)

            return result.all()

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)
            return []


async def get_user_transaction_info(start_period: datetime, end_period: datetime) -> Union[List[Union[tables.Transaction, tables.User]], List]:
    """Транзакции сгруппированные по id и description"""
    async with async_engine.connect() as session:

        try:
            stmt = (
                select(
                    tables.Transaction.id,
                    tables.User.username,
                    func.sum(tables.Transaction.number).label("number")
                )
                .join(tables.User, tables.Transaction.id == tables.User.id)
                .filter(
                    tables.Transaction.updated >= start_period,
                    tables.Transaction.updated < end_period,
                )
                .group_by(tables.Transaction.id, tables.User.username)
                .order_by(tables.Transaction.id, tables.User.username)
            )

            result = await session.execute(stmt)

            return result.all()

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)
            return []


async def get_transaction_info_by_user(user_id: int, start_period: datetime, end_period: datetime) -> Union[List[tables.Transaction], List]:
    """Транзакции сгруппированные по id и description"""
    async with async_engine.connect() as session:

        try:
            stmt = (
                select(
                    tables.Transaction,
                    tables.User.username
                )
                .join(tables.User, tables.Transaction.id == tables.User.id)
                .filter(
                    tables.Transaction.updated >= start_period,
                    tables.Transaction.updated < end_period,
                    tables.Transaction.id == user_id,
                )
                .order_by(tables.Transaction.uid)

            )

            result = await session.execute(stmt)

            return result.all()

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)
            return []

async def get_transaction_info(start_period: datetime, end_period: datetime) -> Union[List[Union[tables.Transaction, tables.User]], List]:
    """Транзакции сгруппированные по id и description"""
    async with async_engine.connect() as session:

        try:
            stmt = (
                select(
                    tables.Transaction,
                    tables.User.username
                )
                .join(tables.User, tables.Transaction.id == tables.User.id)
                .filter(
                    tables.Transaction.updated >= start_period,
                    tables.Transaction.updated < end_period,
                )
                .order_by(tables.Transaction.uid)

            )

            result = await session.execute(stmt)

            return result.all()

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)
            return []


if __name__ == '__main__':
    pass
