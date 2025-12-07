"""
Модуль регистрации команд Telegram-бота для приватных чатов.

Содержит обработчики команд /start, /id и /help с динамическими
клавиатурами и локализацией.
"""

from typing import Any, Dict

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.core.bot.routers.filters import ChatTypeFilter
from app.core.bot.services.keyboards import kb_delete
from app.core.bot.services.logger import log
from app.core.bot.services.multi import multi
from app.core.bot.services.multi.handlers.success import handler_success

user_command: Router = Router()


@user_command.message(
    ChatTypeFilter(chat_type=["private"]),
    Command("start")
)
async def cmd_start(
    message: types.Message,
    state: FSMContext
) -> None:
    """Обрабатывает команду /start.

    Получает текст и клавиатуру из локализации по ключу команды
    и отправляет сообщение с динамической клавиатурой или вызывает
    handler_success при специальном состоянии.

    Args:
        message (types.Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    user_db: Any = user_data.get("user_db")

    if not message.from_user:
        return

    user_state: list = user_db.state[-1]

    if not isinstance(user_state, str):
        return

    msg_id: int = user_db.msg_id
    user_db.msg_id = message.message_id + 1
    await state.update_data(user_db=user_db)

    if user_state != "100":
        text_message: str
        keyboard_message: types.InlineKeyboardMarkup
        link_opts: types.LinkPreviewOptions

        text_message, keyboard_message, link_opts = await multi(
            loc=loc,
            value=user_state,
            tg_id=message.from_user.id
        )

        await message.answer(
            text=text_message,
            reply_markup=keyboard_message,
            link_preview_options=link_opts
        )
    else:
        await handler_success(
            loc=loc,
            tg_id=message.from_user.id,
            event=message,
            user=user_db
        )
    if message.bot:
        if isinstance(msg_id, int) and msg_id != 0:
            try:
                await message.bot.delete_message(message.chat.id, msg_id)
            except BaseException:
                pass

    await log(message)


@user_command.message(
    ChatTypeFilter(chat_type=["private"]),
    Command("id")
)
async def cmd_id(
    message: types.Message,
    state: FSMContext
) -> None:
    """Отправляет ID текущего чата с шаблоном текста и кнопкой удаления.

    Args:
        message (types.Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not loc:
        return

    text_prefix: Any
    text_suffix: Any
    text_prefix, text_suffix = loc.messages.template.id
    text: str = f"{text_prefix}{message.chat.id}{text_suffix}"

    await message.answer(
        text=text,
        reply_markup=kb_delete(loc.buttons)
    )

    await log(message)


@user_command.message(
    ChatTypeFilter(chat_type=["private"]),
    Command("help")
)
async def cmd_help(
    message: types.Message,
    state: FSMContext
) -> None:
    """Отправляет пользователю контакты админов с помощью кнопок.

    Args:
        message (types.Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM для хранения данных пользователя.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not loc:
        return

    await message.answer(
        text=loc.messages.help,
        reply_markup=kb_delete(buttons=loc.buttons)
    )

    await log(message)
