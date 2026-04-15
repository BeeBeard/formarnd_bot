# Модуль парсинга, и записи базовых данных бота по его токену

# from app.bot import BOT, DP
import json
import re
from dataclasses import dataclass
from typing import Union
from aiohttp import ClientSession
import requests
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import BotCommand
from dotenv import load_dotenv
from loguru import logger

from app.config import CONFIG

load_dotenv()

@dataclass(frozen=False)
class BotData:  # Данные бота

    b = None
    id: Union[int, None] = None
    title: str = ""
    name: str = ""
    url: str = ""
    start_url: str = ""
    add_url: str = ""
    session = None

    def __init__(self, token: str = None, proxy: str = "socks5://F7f74d:6hxDPb@45.157.123.53:8000"):
        self.proxy = proxy
        self.token: str = token

    async def init(self):
        logger.debug(f"Запуск инициализации бота")
        if self.check_token():

            if await self.get_session():
                await self.get_info()
                return await self.set_bot()
        raise ValueError(f"Не удалось запустить бота")

    def check_token(self):
        if self.token and re.findall(r'^\d{10}:[\w\W]{35}', self.token):
            return True
        return False

    async def get_session(self):
        self.session = AiohttpSession(proxy=self.proxy)
        return self.session

    async def set_bot(self):

        self.id = int(self.token.split(":")[0])

        self.b = Bot(
            token=self.token,
            session=self.session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        return self

    async def get_info(self):
        async with ClientSession() as session:
            async with session.get(
                f"https://api.telegram.org/bot{self.token}/getMe",
                proxy=self.proxy
            ) as resp:
                content = await resp.json()
                logger.error(content)
                # content = json.loads(result.content.decode('utf8'))
                self.title = content["result"]["first_name"]
                self.name = content["result"]["username"]
                self.url = f"https://t.me/{self.name}"  # НЕ менять привязан к БОТУ!
                self.start_url = f"{self.url}?start="
                self.add_url = f"t.me/{self.name}?startgroup"

    def set_commands(self) -> None:
        """Отобразить список команд для пользователя"""
        commands = [
            BotCommand(command=f"/start", description="Запуск бота"),
            BotCommand(command=f"/id", description="Узнать собственный user.id"),

        ]
        self.b.set_my_commands(commands)


BOT = BotData(token=CONFIG.bot.token.get_secret_value())
# BOT.start_bot()




logger.info(f"Bot id: {BOT.id}")
logger.info(f"Bot title: {BOT.title}")
logger.info(f"Bot name: {BOT.name}")
logger.info(f"Bot url: {BOT.url}")

