"""
Модуль регистрации команд Telegram-бота для приватных чатов.

Содержит обработчики команд /start, /cancel, /id и /help
с динамическими клавиатурами и локализацией.
"""

from typing import Any, Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.core.bot.routers.filters import ChatTypeFilter
from app.core.bot.services.keyboards import kb_delete
from app.core.bot.services.logger import log
from app.core.bot.services.multi import multi
from app.core.bot.services.multi.handlers.send import handle_send
from app.core.bot.services.requests.user import manage_user, manage_user_state
from app.core.database.models.user import User

router: Router = Router()


@router.message(
    ChatTypeFilter(chat_type=["private"]),
    Command("start")
)
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

    if not isinstance(db_user, User) or not isinstance(value, str):
        return

    msg_id: User | bool | None | int = await manage_user(
        tg_id=message.from_user.id,
        action="msg_update",
        msg_id=message.message_id + 1
    )

    if not value == "100":
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
    else:
        await handle_send(
            loc=loc,
            tg_id=message.from_user.id,
            event=message
        )

    if isinstance(msg_id, int) and msg_id != 0 and message.bot:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except BaseException:
            pass

    await log(message)


@router.message(
    ChatTypeFilter(chat_type=["private"]),
    Command("id")
)
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
        reply_markup=kb_delete(loc.button)
    )

    await log(message)


@router.message(
    ChatTypeFilter(chat_type=["private"]),
    Command("help")
)
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
        reply_markup=kb_delete(buttons=loc.button)
    )

    await log(message)
