from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.assistant import Transform, get_int_from_str, print_state_data
from app.bot.content import BotKeyboards, BotStates, BotCmd, BotKeyWords, BotMessages
from app.bot.filters import IsCallCmd
from app.conn import tables, sql
from loguru import logger
# from app.bot.content import BotKeyboards
from datetime import datetime


r_any = Router(name="r_private_any")
r_any.message.filter(F.chat.type.in_({"private"}))


# Отработка команд
# async def echo(msg: Message) -> None:
#     """Тестовая функция для проверки работы бота"""
#
#     user = msg.from_user.username or msg.from_user.first_name
#     await msg.answer(f"{user}, Вы написали в ЛС ({msg.chat.type})")


# Стартовая функция
async def cmd_start(msg: Message) -> None:
    """Тестовая функция для проверки вызова функции через команду /start"""

    try:
        user_data = msg.from_user.model_dump(exclude_none=True)
        user_data["user_id"] = msg.from_user.id

        await sql.to_table(table=tables.User, **user_data)

    except Exception as e:
        logger.error(f"Ошибка при сохранении данных пользователя: {e}")

    user = msg.from_user.username or msg.from_user.first_name
    await msg.answer(
        text=f"{user}, Бот активирован",
        reply_markup=BotKeyboards.start_menu_keyboard()
    )


# 1 Запрос ввода сумм
async def print_arrival(msg: Message, state: FSMContext):
    await state.set_state(BotStates.arrival.state)  # Меняем состояние бота на state_test
    await msg.answer(text="Укажите приход (числом)")


async def print_expense(msg: Message, state: FSMContext):
    await state.set_state(BotStates.expense.state)  # Меняем состояние бота на state_test
    await msg.answer(text="Укажите расход (числом)")

# 2 Сохранение сумм запрос ввода адреса
async def save_arrival(msg: Message, state: FSMContext):

    _arrival = get_int_from_str(msg.text)
    if not _arrival:
        await msg.answer(text="Не найдено число")
        return await print_arrival(msg, state)

    await state.update_data(number=_arrival)
    await print_state_data(state)
    await state.set_state(BotStates.address.state)
    await msg.answer(text="Укажите адрес", reply_markup=BotKeyboards.no_address())


async def save_expense(msg: Message, state: FSMContext):

    _arrival = get_int_from_str(msg.text)
    if not _arrival:
        await msg.answer(text="Не найдено число")

    await state.update_data(number=_arrival * -1)
    await print_state_data(state)
    await state.set_state(BotStates.address.state)
    await msg.answer(text="Укажите адрес", reply_markup=BotKeyboards.no_address())


# 3 Ввод или отказ ввода адреса
async def save_address(msg: Message, state: FSMContext):
    await state.update_data(address=msg.text)
    await print_state_data(state)
    await state.set_state(BotStates.project.state)
    await msg.answer(text="Название проекта", reply_markup=BotKeyboards.no_project())


async def after_click_cmd_no_address(callback: CallbackQuery, state: FSMContext, tform: Transform) -> None:
    await state.update_data(address=None)
    await print_state_data(state)
    await state.set_state(BotStates.project.state)
    await BotKeyboards.edit_as_answered(callback, "Без адреса")
    await callback.message.answer(text="Название проекта", reply_markup=BotKeyboards.no_project())


# 4 Ввод или отказ ввода проекта
async def save_project(msg: Message, state: FSMContext):
    await state.update_data(project=msg.text)
    await print_state_data(state)
    await state.set_state(BotStates.description.state)
    await msg.answer(text="Ведите описание")


async def after_click_cmd_no_project(callback: CallbackQuery, state: FSMContext, tform: Transform) -> None:
    await state.update_data(project=None)
    await print_state_data(state)
    await state.set_state(BotStates.description.state)
    await BotKeyboards.edit_as_answered(callback, "Без проекта")
    await callback.message.answer(text="Ведите описание")


# 5 Ввод описания
async def save_description(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text)
    await print_state_data(state)
    await state.set_state(BotStates.comment.state)
    await msg.answer(text="Ведите комментарий", reply_markup=BotKeyboards.no_comment())


# 6 Ввод или отказ ввода комментария КОНЕЦ ЗАПОЛНЕНИЯ
async def save_comment(msg: Message, state: FSMContext):
    await state.update_data(comment=msg.text)
    data = await print_state_data(state)
    text = BotMessages.get_final_info(f"@{msg.from_user.username}", data)
    await msg.answer(text=text, reply_markup=BotKeyboards.save_ro_no_save())


async def after_click_cmd_no_comment(callback: CallbackQuery, state: FSMContext, tform: Transform) -> None:
    await state.update_data(comment=None)
    data = await print_state_data(state)
    await BotKeyboards.edit_as_answered(callback, "Без комментария")

    text = BotMessages.get_final_info(f"@{callback.message.from_user.username}", data)
    await callback.message.answer(text=text, reply_markup=BotKeyboards.save_ro_no_save())

# 7 Сохранить или нет
async def after_click_cmd_yes_save(callback: CallbackQuery, state: FSMContext, tform: Transform) -> None:

    to_save = await print_state_data(state)
    to_save["id"] = callback.message.chat.id

    await sql.to_table(table=tables.Transaction, **to_save)
    # SAVE SQL
    await state.clear()
    await BotKeyboards.edit_as_answered(callback, "Сохранено")
    # await callback.message.answer(text=f"Данные сохранены")


async def after_click_cmd_no_save(callback: CallbackQuery, state: FSMContext, tform: Transform) -> None:
    # NO SAVE SQL
    await state.clear()
    await BotKeyboards.edit_as_answered(callback, "Ввод отменен")
    # await callback.message.answer(text=f"Ввод отменен")


#  2.1 Получить информацию за период
async def print_info(msg: Message, state: FSMContext):

    await state.set_state(BotStates.start_period.state)
    await msg.answer(text="Укажите дату начала выборки в формате ГГГГ-ММ-ДД")


# 2.2 Сохранить начало выборки
async def save_start_period(msg: Message, state: FSMContext):

    try:
        date_obj = datetime.strptime(msg.text, "%Y-%m-%d")  # Преобразует в datetime
        logger.info(date_obj)
    except Exception as e:
        logger.error(e)
        await msg.answer(text="Не верно введена дата")
        return await print_info(msg, state)

    await state.update_data(start_period=date_obj)
    data = await print_state_data(state)

    await state.set_state(BotStates.end_period.state)
    await msg.answer(text="Укажите день окончания выборки в формате ГГГГ-ММ-ДД (указанный день не будет учитываться)")

# 2.3 Сохранить конец выборки
async def save_end_period(msg: Message, state: FSMContext):

    try:
        date_obj = datetime.strptime(msg.text, "%Y-%m-%d")  # Преобразует в datetime
        logger.info(date_obj)
    except Exception as e:
        logger.error(e)
        await msg.answer(text="Не верно введена дата")
        return await print_info(msg, state)

    await state.update_data(end_period=date_obj)

    data = await print_state_data(state)
    await state.clear()

    db_data_user = await sql.get_transaction_info(data["start_period"], data["end_period"])
    if not db_data_user:
        text = f"За указанный период транзакций нет"
        return await msg.answer(text=text)

    db_data_group = await sql.get_group_transaction_info(data["start_period"], data["end_period"])
    row_data_group = [
        f"{i} - <b>Сумма:</b> {row.number}, @{row.username}, <b>Описание:</b> {row.description}"
        for i, row in enumerate(db_data_group)
    ]

    text = "<i>Транзакции в разбивке по пользователю и описанию:</i>\n" + "\n".join(row_data_group)
    text += "\n\n"

    db_data_user = await sql.get_user_transaction_info(data["start_period"], data["end_period"])
    row_data = [
        f"{i} - <b>Сумма:</b> {row.number}, @{row.username}"
        for i, row in enumerate(db_data_user)
    ]
    text += "<i>Транзакции в разбивке по пользователю:</i>\n" + "\n".join(row_data)
    text += "\n\n"

    text += f"<i>Сумма за указанный период:</i> {db_data_user[0].number}"
    await msg.answer(text=text)


# Отработка вводимых команд
r_any.message.register(cmd_start, Command("start"))


# Отработка обычных кнопок
r_any.message.register(print_arrival,   F.text == BotKeyWords.arrival)
r_any.message.register(print_expense,   F.text == BotKeyWords.expense)
r_any.message.register(print_info,      F.text == BotKeyWords.info)

# Отработка state
r_any.message.register(save_arrival,        StateFilter("BotStates:arrival"))
r_any.message.register(save_expense,        StateFilter("BotStates:expense"))
r_any.message.register(save_address,        StateFilter("BotStates:address"))
r_any.message.register(save_project,        StateFilter("BotStates:project"))
r_any.message.register(save_description,    StateFilter("BotStates:description"))
r_any.message.register(save_comment,        StateFilter("BotStates:comment"))


r_any.message.register(save_start_period,   StateFilter("BotStates:start_period"))
r_any.message.register(save_end_period,     StateFilter("BotStates:end_period"))


# Отработка нажатий кнопок в сообщениях
r_any.callback_query.register(after_click_cmd_no_address,   IsCallCmd(BotCmd.no_address))
r_any.callback_query.register(after_click_cmd_no_project,   IsCallCmd(BotCmd.no_project))
r_any.callback_query.register(after_click_cmd_no_comment,   IsCallCmd(BotCmd.no_comment))
r_any.callback_query.register(after_click_cmd_yes_save,     IsCallCmd(BotCmd.yes_save))
r_any.callback_query.register(after_click_cmd_no_save,      IsCallCmd(BotCmd.no_save))


if __name__ == '__main__':
    pass
