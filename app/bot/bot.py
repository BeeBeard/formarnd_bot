# Модуль парсинга, и записи базовых данных бота по его токену

# from app.bot import BOT, DP
import json
import re
from dataclasses import dataclass
from typing import Union

import requests
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import BotCommand
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
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

    def __init__(self, token: str = None):

        self.token: str = token

        if self.check_token():
            # self.set_bot()
            self.get_info()

    async def init(self):
        await self.set_bot()



    def check_token(self):
        if self.token and re.findall(r'^\d{10}:[\w\W]{35}', self.token):
            return True
        return False

    async def set_bot(self):

        proxy = "socks5://F7f74d:6hxDPb@45.157.123.53:8000"

        connector = ProxyConnector.from_url(proxy)

        session = ClientSession(connector=connector)

        self.id = int(self.token.split(":")[0])

        self.b = Bot(
            token=self.token,
            session=session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

    def get_info(self):

        url = f"https://api.telegram.org/bot{self.token}/getMe"
        result = requests.get(url=url)
        content = json.loads(result.content.decode('utf8'))
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

