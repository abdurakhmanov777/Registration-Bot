"""
Модуль регистрации команд Telegram-бота для приватных чатов.

Содержит обработчики команд /start, /cancel, /id и /help
с динамическими клавиатурами и локализацией.
"""

from typing import Any, Callable, Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.bot.routers.filters import ChatTypeFilter
from app.bot.services.keyboards import help, kb_delete
from app.bot.services.logger import log
from app.bot.services.multi import multi
from app.bot.services.requests.data import manage_data_clear
from app.bot.services.requests.user import manage_user, manage_user_state
from app.database.models.user import User

router: Router = Router()


def user_command(
    *commands: str
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Декоратор для регистрации команд, доступных только в приватных чатах.

    Args:
        *commands (str): Названия команд для фильтрации.

    Returns:
        Callable: Декоратор для функции-обработчика.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return router.message(
            ChatTypeFilter(chat_type=["private"]),
            Command(*commands)
        )(func)

    return decorator


@user_command("start")
async def cmd_start(
    message: Message,
    state: FSMContext
) -> None:
    """
    Обрабатывает команду /start.

    Получает текст и клавиатуру из локализации по ключу команды
    и отправляет сообщение с динамической клавиатурой.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not loc or not message.from_user:
        return

    value: bool | str | list[str] | None = await manage_user_state(
        message.from_user.id,
        "peek"
    )

    db_user: User | bool | None | int = await manage_user(
        tg_id=message.from_user.id,
        action="get",
    )
    if not isinstance(db_user, User):
        return

    msg_id: User | bool | None | int = await manage_user(
        tg_id=message.from_user.id,
        action="msg_update",
        msg_id=message.message_id + 1
    )

    if not isinstance(value, str):
        return

    text_message: str
    keyboard_message: InlineKeyboardMarkup
    text_message, keyboard_message = await multi(
        loc=loc,
        value=value,
        tg_id=message.from_user.id
    )

    await message.answer(
        text=text_message,
        reply_markup=keyboard_message
    )

    if isinstance(msg_id, int) and msg_id != 0 and message.bot:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception as e:
            print(e)

    await log(message)


@user_command("cancel")
async def cmd_cancel(
    message: Message,
    state: FSMContext
) -> None:
    """
    Обрабатывает команду /cancel.

    Очищает состояние пользователя и отправляет сообщение
    с клавиатурой по умолчанию.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not loc or not message.from_user:
        return

    await manage_user_state(
        message.from_user.id,
        "clear"
    )
    await manage_data_clear(tg_id=message.from_user.id)
    text_message: str
    keyboard_message: InlineKeyboardMarkup
    text_message, keyboard_message = await multi(
        loc=loc,
        value='1',
        tg_id=message.from_user.id
    )

    await message.answer(
        text=text_message,
        reply_markup=keyboard_message
    )

    msg_id: User | bool | None | int = await manage_user(
        tg_id=message.from_user.id,
        action="msg_update",
        msg_id=message.message_id + 1
    )
    if isinstance(msg_id, int) and msg_id != 0 and message.bot:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except Exception as e:
            print(e)

    await log(message)


@user_command("id")
async def cmd_id(
    message: Message,
    state: FSMContext
) -> None:
    """
    Отправляет ID текущего чата с шаблоном текста и кнопкой удаления.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not loc:
        return

    text_prefix: Any
    text_suffix: Any
    text_prefix, text_suffix = loc.template.id
    text: str = f"{text_prefix}{message.chat.id}{text_suffix}"

    await message.answer(
        text=text,
        reply_markup=kb_delete
    )

    await log(message)


@user_command("help")
async def cmd_help(
    message: Message,
    state: FSMContext
) -> None:
    """
    Отправляет контакты админов с помощью кнопок.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not loc:
        return

    await message.answer(
        text=loc.help,
        reply_markup=help
    )

    await log(message)
