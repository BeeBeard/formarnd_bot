# Список переменный для cmd callback

from typing import Union

from aiogram.filters.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.assistant import Transform
from app.bot import BOT
from aiogram.fsm.context import FSMContext


class BotCmd:
    """Класс для описания переменных используемых при вызове команд в боте"""
    no_address = "no_address"
    no_project = "no_project"
    no_comment = "no_comment"
    no_save = "no_save"
    yes_save = "yes_save"

    empty = "empty"


# Текста кнопок
class BotKeyWords:
    """Клас для описания переменных используемых для клавиатуры в телеграмме"""

    arrival = "Приход"
    expense = "Расход"
    info = "Получить расчет"


class BotStates(StatesGroup):
    """Клас для хранения списка используемых состояний"""

    # 1 Блок
    arrival = State()
    expense = State()

    address = State()
    project = State()
    description = State()
    comment = State()

    # 2 Блок
    info = State()
    start_period = State()  # Начало выборки
    end_period = State()    # Конец выборки


class BotKeyboards:
    """Класс для создания клавиатур"""

    # @staticmethod
    # def test_show_menu(value: Union[str, int]) -> InlineKeyboardMarkup:  # Клавиатура под сообщением ботом
    #     event_menu = InlineKeyboardBuilder()
    #     event_menu.button(text=BotKeyWords.expense, callback_data=Transform(cmd=BotCmd.cmd_test1, value=value).str)
    #     event_menu.adjust(1)
    #     return event_menu.as_markup()
    #
    # @staticmethod
    # def test_show_state() -> InlineKeyboardMarkup:  # Клавиатура под сообщением ботом
    #     event_menu = InlineKeyboardBuilder()
    #     event_menu.button(text=BotKeyWords.expense, callback_data=Transform(cmd=BotCmd.cmd_test2).str)
    #     event_menu.adjust(1)
    #     return event_menu.as_markup()

    @staticmethod
    def no_address():
        buttons = [[
            InlineKeyboardButton(
                text="Не указывать адрес",
                callback_data=Transform(cmd=BotCmd.no_address).str)
            ]]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def no_project():
        buttons = [[
            InlineKeyboardButton(
                text="Не указывать проект",
                callback_data=Transform(cmd=BotCmd.no_project).str)
            ]]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def no_comment():
        buttons = [[
            InlineKeyboardButton(
                text="Не указывать комментарий",
                callback_data=Transform(cmd=BotCmd.no_comment).str)
            ]]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def save_ro_no_save():
        buttons = [[
            InlineKeyboardButton(text="Сохранить", callback_data=Transform(cmd=BotCmd.yes_save).str),
            InlineKeyboardButton(text="Не сохранять", callback_data=Transform(cmd=BotCmd.no_save).str)
            ]]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def start_menu_keyboard() -> ReplyKeyboardMarkup:  # Клавиатура управления ботом

        kb = [[
            KeyboardButton(text=BotKeyWords.arrival),
            KeyboardButton(text=BotKeyWords.expense)
        ], [
            KeyboardButton(text=BotKeyWords.info)

        ]
        ]
        return ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
        )

    @staticmethod
    async def edit_as_answered(callback: CallbackQuery, name: str = None) -> str:
        # Редактируем предыдущее сообщение так что остается только нажатая кнопка (callback = empty)
        await callback.answer()

        buttons = []
        button_text = ""

        tform = Transform(callback.data)
        if isinstance(tform.value, int):
            value = tform.value + 1
        else:
            value = 1

        for row in callback.message.reply_markup.inline_keyboard:
            for coll in row:
                if coll.callback_data == callback.data:
                    button_text = name if name else coll.text
                    buttons = [[InlineKeyboardButton(text=button_text, callback_data=Transform(cmd=BotCmd.empty, value=value).str)]]

                    break
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await BOT.b.edit_message_reply_markup(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=keyboard)
        return button_text

class BotMessages:

    @staticmethod
    def get_final_info(username: str, data: dict):

        author = f"{username}"
        summ = f"<b>Сумма</b>: {data['number']}\n" if data["number"] else ""
        address = f"<b>Адрес</b>: {data['address']}\n" if data["address"] else ""
        project = f"<b>Проект</b>: {data['project']}\n" if data["project"] else ""
        description = f"<b>Описание</b>: {data['description']}\n" if data["description"] else ""
        comment = f"<b>Комментарий</b>: {data['comment']}\n" if data["comment"] else ""

        text = (
            f"<b>Данные для записи:</b>\n"
            f"<b>Автор</b>: {author}\n"
            f"{summ}{address}{project}{description}{comment}"
        )

        return text


    start = f"Тестовое стартовое сообщений"


if __name__ == '__main__':
    pass
