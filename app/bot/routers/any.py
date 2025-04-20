from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.assistant import Transform, get_int_from_str, print_state_data
from app.bot.content import BotKeyboards, BotStates, BotCmd, BotKeyWords, BotMessages
from app.bot.filters import IsCallCmd
from app.conn import tables, sql
from loguru import logger
from app.bot import BOT
from datetime import datetime


r_any = Router(name="r_private_any")

async def cmd_id(msg: Message) -> None:
    """Тестовая функция для проверки вызова функции через команду /start"""
    await msg.answer(
        text=f"Ваш ID: {msg.from_user.id}",
    )

async def cmd_delete(msg: Message) -> None:
    """Удаление транзакции"""

    try:
        uid = msg.text.split(" ")[1]
        result = await sql.delete_transaction(uid)
        text = f"Транзакция {uid} удалена" if result else f"Транзакция {uid} не найдена"
        await msg.answer(text)
        await msg.delete()

    except Exception as e:
        logger.error(e)
        text = f"Не удалось выполнить операцию"
        await msg.answer(text)
        await msg.delete()


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

# 0.1 После нажатия на отмену ввода

async def after_click_cmd_clear(callback: CallbackQuery, state: FSMContext, tform: Transform) -> None:
    await state.clear()
    await callback.message.delete()


# 1 Запрос ввода сумм
async def print_arrival(msg: Message, state: FSMContext):
    await state.update_data(id=msg.from_user.id)
    await state.set_state(BotStates.arrival.state)  # Меняем состояние бота на state_test
    bot_msg = await msg.answer(text="Укажите приход (числом)", reply_markup=BotKeyboards.get_clear())
    await state.update_data(message_id=bot_msg.message_id)
    await msg.delete()

async def print_expense(msg: Message, state: FSMContext):
    await state.update_data(id=msg.from_user.id)
    await state.set_state(BotStates.expense.state)  # Меняем состояние бота на state_test
    bot_msg = await msg.answer(text="Укажите расход (числом)", reply_markup=BotKeyboards.get_clear())
    await state.update_data(message_id=bot_msg.message_id)
    await msg.delete()

# 01 Сохраняем расход
async def save_expense(msg: Message, state: FSMContext):

    _arrival = get_int_from_str(msg.text)
    if not _arrival:
        await msg.delete()
        return await print_arrival(msg, state)

    await state.update_data(number=_arrival * -1)
    data = await print_state_data(state)
    await state.set_state(BotStates.description.state)
    bot_msg = await msg.answer(text="Введите описание", reply_markup=BotKeyboards.get_clear())

    await BOT.b.delete_message(chat_id=msg.chat.id, message_id=data["message_id"])
    await msg.delete()
    await state.update_data(message_id=bot_msg.message_id)


# 01 Сохраняем доход
async def save_arrival(msg: Message, state: FSMContext):

    _arrival = get_int_from_str(msg.text)
    if not _arrival:
        await msg.delete()
        return await print_arrival(msg, state)

    await state.update_data(number=_arrival)
    data = await print_state_data(state)
    await state.set_state(BotStates.description.state)
    bot_msg = await msg.answer(text="Введите описание", reply_markup=BotKeyboards.get_clear())

    await BOT.b.delete_message(chat_id=msg.chat.id, message_id=data["message_id"])
    await msg.delete()
    await state.update_data(message_id=bot_msg.message_id)


# 3 Сохраняем описание
async def save_description(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text)
    data = await print_state_data(state)
    await state.set_state(BotStates.project.state)
    bot_msg = await msg.answer(text="Укажите проект", reply_markup=BotKeyboards.no_project())
    await BOT.b.delete_message(chat_id=msg.chat.id, message_id=data["message_id"])
    await msg.delete()
    await state.update_data(message_id=bot_msg.message_id)


# 4 Сохраняем проект и выводим стату
async def save_project(msg: Message, state: FSMContext):
    await state.update_data(project=msg.text)
    data = await print_state_data(state)
    text = BotMessages.get_final_info(f"@{msg.from_user.username}", data)
    bot_msg = await msg.answer(text=text, reply_markup=BotKeyboards.save_ro_no_save())
    await BOT.b.delete_message(chat_id=msg.chat.id, message_id=data["message_id"])
    await msg.delete()
    await state.update_data(message_id=bot_msg.message_id)

# 4 Пропускаем проект и выводим стату
async def after_click_cmd_no_project(callback: CallbackQuery, state: FSMContext, tform: Transform) -> None:
    await state.update_data(project=None)
    data = await print_state_data(state)
    text = BotMessages.get_final_info(f"@{callback.message.from_user.username}", data)
    bot_msg = await callback.message.answer(text=text, reply_markup=BotKeyboards.save_ro_no_save())
    await BOT.b.delete_message(chat_id=callback.message.chat.id, message_id=data["message_id"])
    await state.update_data(message_id=bot_msg.message_id)


# 7 Сохранить или нет
async def after_click_cmd_yes_save(callback: CallbackQuery, state: FSMContext, tform: Transform) -> None:

    to_save = await print_state_data(state)

    result = await sql.to_table(table=tables.Transaction, **to_save)
    # SAVE SQL
    if result:
        await state.clear()
        await BotKeyboards.edit_as_answered(callback, "Сохранено")
        return
    await state.clear()
    await callback.message.answer(f"Не удалось сохранить транзакцию")
    await callback.message.delete()


async def after_click_cmd_no_save(callback: CallbackQuery, state: FSMContext, tform: Transform) -> None:
    # NO SAVE SQL
    await state.clear()
    await callback.message.delete()


#  2.1 Получить информацию за период
async def print_info(msg: Message, state: FSMContext):

    await state.set_state(BotStates.start_period.state)
    bot_msg = await msg.answer(
        text="Укажите дату начала выборки в формате ГГГГ-ММ-ДД",
        reply_markup=BotKeyboards.get_clear()
    )
    await msg.delete()
    await state.update_data(message_id=bot_msg.message_id)

# 2.2 Сохранить начало выборки
async def save_start_period(msg: Message, state: FSMContext):

    await msg.delete()

    try:
        date_obj = datetime.strptime(msg.text, "%Y-%m-%d")  # Преобразует в datetime
        logger.info(date_obj)
    except Exception as e:
        logger.error(e)
        return await print_info(msg, state)

    await state.update_data(start_period=date_obj)
    data = await print_state_data(state)
    await state.set_state(BotStates.end_period.state)

    bot_msg = await msg.answer(
        text="Укажите день окончания выборки в формате ГГГГ-ММ-ДД",
        reply_markup=BotKeyboards.get_clear()
    )
    await BOT.b.delete_message(chat_id=msg.chat.id, message_id=data["message_id"])
    await state.update_data(message_id=bot_msg.message_id)

# 2.3 Сохранить конец выборки
async def save_end_period(msg: Message, state: FSMContext):

    await msg.delete()

    try:
        date_obj = datetime.strptime(msg.text, "%Y-%m-%d")  # Преобразует в datetime
        logger.info(date_obj)
    except Exception as e:
        logger.error(e)
        return await print_info(msg, state)

    await state.update_data(end_period=date_obj)

    data = await print_state_data(state)
    await BOT.b.delete_message(chat_id=msg.chat.id, message_id=data["message_id"])
    await state.clear()

    dc_data = await sql.get_transaction_info(data["start_period"], data["end_period"])
    if not dc_data:
        text = f"За указанный период транзакций нет"
        return await msg.answer(text=text)

    r_any.message.register(save_arrival, StateFilter("BotStates:arrival"))
    r_any.message.register(save_expense, StateFilter("BotStates:expense"))
    _L = []
    _arrival = []
    _expense = []
    _summ_arrival = 0
    _summ_expense = 0
    for i, v in enumerate(dc_data):
        project = f" 🚀 {v.project}" if v.project else ""
        if v.number > 0:
            _arrival.append(f"<b>{v.uid}</b>: <b> ₽ {v.number}</b> 👤@{v.username} {project} 📝 {v.description}")
            _summ_arrival += v.number
        else:
            _expense.append(f"<b>{v.uid}</b>: <b> ₽ {v.number}</b> 👤@{v.username} {project} 📝 {v.description}")
            _summ_expense += v.number

    text = "<b>Транзакции за указанный период:</b>\n\n"
    text += "<b>Приход:\n</b>" + "\n".join(_arrival) + "\n\n" if _arrival else ""
    text += "<b>Расход:\n</b>" + "\n".join(_expense) + "\n\n" if _expense else ""
    text += f"<b>Итого приход: {_summ_arrival}</b>\n"
    text += f"<b>Итого расход: {_summ_expense}</b>\n"
    text += f"<b>Итого за указанный период: {_summ_arrival + _summ_expense}</b>"
    await msg.answer(text=text)

    _users = list(set([i.id for i in dc_data]))
    logger.info(_users)

    for user in _users:

        dc_data_user = await sql.get_transaction_by_user(user, data["start_period"], data["end_period"])
        _L = []
        _summ = 0
        for i, v in enumerate(dc_data_user):
            project = f" 🚀 {v.project}" if v.project else ""
            _L.append(f"<b>{v.uid}</b>: <b> ₽ {v.number}</b> {project} 📝 {v.description}")
            _summ += v.number

            text = f"<b>👤 Транзакции @{v.username} за указанный период</b>\n\n"
            text += "\n".join(_L)
            text += "\n\n"
            text += f"<b>Итого за указанный период: {_summ}</b>"
        await msg.answer(text=text)


# Отработка вводимых команд
r_any.message.register(cmd_start,           Command("start"))
r_any.message.register(print_info,          Command("info"))
r_any.message.register(cmd_id,              Command("if"))

r_any.message.register(print_arrival,       Command("+"))
r_any.message.register(print_expense,       Command("-"))
r_any.message.register(cmd_delete,          Command("del"))


# Отработка обычных кнопок
r_any.message.register(print_arrival,   F.text == BotKeyWords.arrival)
r_any.message.register(print_expense,   F.text == BotKeyWords.expense)
r_any.message.register(print_info,      F.text == BotKeyWords.info)

# Отработка state
r_any.message.register(save_arrival,        StateFilter("BotStates:arrival"))
r_any.message.register(save_expense,        StateFilter("BotStates:expense"))
r_any.message.register(save_description,    StateFilter("BotStates:description"))
r_any.message.register(save_project,        StateFilter("BotStates:project"))

r_any.message.register(save_start_period,   StateFilter("BotStates:start_period"))
r_any.message.register(save_end_period,     StateFilter("BotStates:end_period"))

# Отработка нажатий кнопок в сообщениях
r_any.callback_query.register(after_click_cmd_clear,        IsCallCmd(BotCmd.clear))
r_any.callback_query.register(after_click_cmd_no_project,   IsCallCmd(BotCmd.no_project))
r_any.callback_query.register(after_click_cmd_yes_save,     IsCallCmd(BotCmd.yes_save))
r_any.callback_query.register(after_click_cmd_no_save,      IsCallCmd(BotCmd.no_save))


if __name__ == '__main__':
    pass
