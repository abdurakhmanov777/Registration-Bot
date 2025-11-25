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
from app.bot.services.requests.user import manage_user, manage_user_state
from app.database.models.user import User

router: Router = Router()


def user_message() -> Callable[
    [Callable[..., Any]], Callable[..., Any]
]:
    """
    Декоратор для регистрации сообщений, доступных только в приватных чатах.

    Args:
        *commands (str): Названия команд для фильтрации.

    Returns:
        Callable: Декоратор для функции-обработчика.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return router.message(
            ChatTypeFilter(chat_type=["private"])
        )(func)

    return decorator


@user_message()
async def msg_user(
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
    if not loc or not message.from_user or not message.bot:
        return

    value: bool | str | list[str] | None = await manage_user_state(
        message.from_user.id,
        "peek"
    )

    db_user: User | bool | None | int = await manage_user(
        tg_id=message.from_user.id,
        action="get",
    )

    if not isinstance(value, str) or not isinstance(db_user, User):
        return

    text_message: str
    keyboard_message: InlineKeyboardMarkup
    text_message, keyboard_message = await multi(
        loc=loc,
        value=value,
        tg_id=message.from_user.id,
        data=message.text
    )

    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=db_user.msg_id,
            text=text_message,
            reply_markup=keyboard_message
        )
    except BaseException:
        pass

    await log(message)
