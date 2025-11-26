"""
Модуль регистрации команд Telegram-бота для приватных чатов.

Содержит обработчики команд /start, /cancel, /id и /help
с динамическими клавиатурами и локализацией.
"""

from functools import wraps
from typing import Any, Callable

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.types import User as TgUser

from app.core.bot.routers.filters import ChatTypeFilter
from app.core.bot.services.keyboards import help, kb_delete
from app.core.bot.services.logger import log
from app.core.bot.services.multi import multi
from app.core.bot.services.multi.handlers.send import handle_send
from app.core.bot.services.requests.data import manage_data_clear
from app.core.bot.services.requests.user import manage_user, manage_user_state
from app.core.bot.utils import ensure
from app.core.database.models import User

router: Router = Router()


# ------------------------- Decorators --------------------------------


def user_command(
    *commands: str
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор для регистрации команд и проверки контекста пользователя.

    Обеспечивает передачу tg_user, bot и loc в хэндлер.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(
            message: Message,
            state: FSMContext,
            *args: Any,
            **kwargs: Any
        ) -> None:
            tg_user: TgUser | None = message.from_user
            bot: Bot | None = message.bot
            state_data: dict[str, Any] = await state.get_data()
            loc: Any | None = state_data.get("loc_user")

            if tg_user is None or bot is None or loc is None:
                return

            kwargs.update({"tg_user": tg_user, "bot": bot, "loc": loc})
            return await func(message, state, *args, **kwargs)

        return router.message(
            ChatTypeFilter(["private"]),
            Command(*commands)
        )(wrapper)

    return decorator


# ---------------------------- Handlers -------------------------------


@user_command("start")
async def cmd_start(
    message: Message,
    state: FSMContext,
    *,
    tg_user: TgUser,
    bot: Bot,
    loc: Any
) -> None:
    """Обрабатывает команду /start и отправляет сообщение с клавиатурой.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM пользователя.
        tg_user (TgUser): Объект Telegram пользователя.
        bot (Bot): Экземпляр бота.
        loc (Any): Локализация пользователя.
    """
    tg_id: int = tg_user.id
    value: str | None = ensure(await manage_user_state(tg_id, "peek"), str)
    db_user: User | None = ensure(await manage_user(tg_id=tg_id, action="get"), User)
    if not value or not db_user:
        return

    msg_id: int | None = ensure(
        await manage_user(
            tg_id=tg_id, action="msg_update", msg_id=message.message_id + 1
        ),
        int,
    )

    if value != "100":
        text: str
        keyboard: InlineKeyboardMarkup
        text, keyboard = await multi(loc=loc, value=value, tg_id=tg_id)
        await message.answer(text=text, reply_markup=keyboard)
    else:
        await handle_send(loc=loc, tg_id=tg_id, event=message)

    if msg_id:
        try:
            await bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass

    await log(message)


@user_command("cancel")
async def cmd_cancel(
    message: Message,
    state: FSMContext,
    *,
    tg_user: TgUser,
    bot: Bot,
    loc: Any
) -> None:
    """Обрабатывает команду /cancel, очищает состояние пользователя
    и отправляет клавиатуру по умолчанию.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM пользователя.
        tg_user (TgUser): Объект Telegram пользователя.
        bot (Bot): Экземпляр бота.
        loc (Any): Локализация пользователя.
    """
    tg_id: int = tg_user.id

    await manage_user_state(tg_id, "clear")
    await manage_data_clear(tg_id=tg_id)

    text: str
    keyboard: InlineKeyboardMarkup
    text, keyboard = await multi(loc=loc, value="1", tg_id=tg_id)
    await message.answer(text=text, reply_markup=keyboard)

    msg_id: int | None = ensure(
        await manage_user(
            tg_id=tg_id, action="msg_update", msg_id=message.message_id + 1
        ),
        int,
    )

    if msg_id:
        try:
            await bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass

    await log(message)


@user_command("id")
async def cmd_id(
    message: Message,
    state: FSMContext,
    *,
    tg_user: TgUser,
    bot: Bot,
    loc: Any
) -> None:
    """Отправляет ID текущего чата с шаблоном текста и кнопкой удаления.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM пользователя.
        tg_user (TgUser): Объект Telegram пользователя.
        bot (Bot): Экземпляр бота.
        loc (Any): Локализация пользователя.
    """
    text_prefix: Any
    text_suffix: Any
    text_prefix, text_suffix = loc.template.id
    text: str = f"{text_prefix}{message.chat.id}{text_suffix}"

    await message.answer(text=text, reply_markup=kb_delete)
    await log(message)


@user_command("help")
async def cmd_help(
    message: Message,
    state: FSMContext,
    *,
    tg_user: TgUser,
    bot: Bot,
    loc: Any
) -> None:
    """Отправляет контакты админов с помощью кнопок.

    Args:
        message (Message): Входящее сообщение Telegram.
        state (FSMContext): Контекст FSM пользователя.
        tg_user (TgUser): Объект Telegram пользователя.
        bot (Bot): Экземпляр бота.
        loc (Any): Локализация пользователя.
    """
    await message.answer(text=loc.help, reply_markup=help)
    await log(message)
