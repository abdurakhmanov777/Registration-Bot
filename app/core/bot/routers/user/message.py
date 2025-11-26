"""
Модуль регистрации команд Telegram-бота для приватных чатов.

Содержит обработчики команд /start, /cancel, /id и /help
с динамическими клавиатурами и локализацией.
"""

from typing import Any, Callable, Dict

from aiogram import Router
from aiogram.filters import BaseFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.core.bot.routers.filters import ChatTypeFilter
from app.core.bot.services.logger import log
from app.core.bot.services.multi import multi
from app.core.bot.services.requests.user import manage_user, manage_user_state
from app.core.database.models.user import User

router: Router = Router()


@router.message(
    ChatTypeFilter(chat_type=["private"])
)
async def msg_user(
    message: Message,
    state: FSMContext
) -> None:
    """
    Обрабатывает команду /start.

    Получает текст и клавиатуру из локализации по ключу команды
    и отправляет сообщение с динамической клавиатурой.
    """
    if not message.from_user or not message.bot:
        return

    # Локализация
    loc: Any | None = (await state.get_data()).get("loc_user")
    if not loc:
        return

    tg_id: int = message.from_user.id

    # Получаем состояние и данные пользователя
    db_user: User | bool | None | int = await manage_user(
        tg_id=tg_id,
        action="get"
    )
    value: bool | str | list[str] | None = await manage_user_state(
        tg_id,
        "peek"
    )

    if not isinstance(db_user, User) or not isinstance(value, str):
        return

    # Проверяем, что состояние соответствует "value"
    state_obj: Any | None = getattr(loc, f"userstate_{value}", None)
    if not state_obj or state_obj.type != "input":
        return

    # Генерация сообщения и клавиатуры
    text_message: str
    keyboard_message: InlineKeyboardMarkup
    text_message, keyboard_message = await multi(
        loc=loc,
        value=value,
        tg_id=tg_id,
        data=message.text
    )

    # Пробуем обновить сообщение
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
