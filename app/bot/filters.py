# Модуль с пользовательскими фильтрами

from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from app.config import CONFIG

from app.assistant import Transform


class IsCallCmd(Filter):

    def __init__(self, cmd: str = None) -> None:
        self.cmd = cmd

    async def __call__(self, msg: CallbackQuery) -> bool:
        cmd = Transform(msg.data).cmd
        if self.cmd == cmd:
            return True
        return False


class IsBotAdmins(Filter):
    """Проверяем, пользователь админ, или супер админ, бота или нет"""
    async def __call__(self, msg: [Message, CallbackQuery]) -> bool:

        if isinstance(msg, CallbackQuery):
            msg = msg.message

        user_id = msg.chat.id if msg.chat.type == "private" else msg.from_user.id

        if not CONFIG.bot.user_ids:
            return True

        if user_id in CONFIG.bot.user_ids:
            return True
        return False


if __name__ == '__main__':
    pass
