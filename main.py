import asyncio
import pprint
import sys

from loguru import logger

from app import start_bot
from app.config import CONFIG
from app.conn import CONN, tables


class LogSetting:

    INFO = (
        "<green>{time:HH:mm:ss}</green> -> "
        "<b>{message}</b>\n")

    EXCEPTION = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | <yellow>[Line {line: >4} | {function: >4} | {file: >4}]:</yellow>\n"
        "<b>{message}</b>\n"
        f"===============\n"
        "{exception}\n"
        f"===============\n")

    ELSE = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | <yellow>[Line {line: >4} | {function: >4} | {file: >4}]:</yellow>\n"
        "<b>{message}</b>\n")

    @staticmethod
    def get_format(record):
        if record["level"].name == "INFO":
            return LogSetting.INFO
        elif record["exception"]:
            return LogSetting.EXCEPTION
        else:
            return LogSetting.ELSE


# logger.remove(handler_id=None)
logger.configure(handlers=[{"sink": sys.stderr, "format": LogSetting.get_format}])

logger.add("logs/.log", rotation="06:00", compression="zip")
logger.add("logs/info/info.log", format=LogSetting.INFO, level="INFO", rotation="06:00", compression="zip")
logger.add("logs/debug/debug.log", format=LogSetting.ELSE, level="DEBUG", rotation="06:00", compression="zip")
logger.add("logs/error/error.log", format=LogSetting.ELSE, level="ERROR", rotation="06:00", compression="zip",
           backtrace=True, diagnose=True, catch=True)


@logger.catch
async def main():

    pprint.pprint(CONFIG.model_dump())
    print()

    logger.info(f"Подключение и настройка базы данных")
    tables.Base.metadata.create_all(CONN.engine)

    logger.info(f"Запуск бота")
    await start_bot()


if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:
        pass

    except Exception as e:
        logger.exception(e)

    logger.info(f"Выключение бота")
