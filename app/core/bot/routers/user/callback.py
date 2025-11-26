"""
Модуль обработки коллбеков пользователя в приватных чатах.

Содержит декоратор для проверки сообщений, бота и локализации,
а также обработчики различных callback кнопок.
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.types import User as TgUser
from aiogram.types.inaccessible_message import InaccessibleMessage

from app.core.bot.routers.filters import CallbackNextFilter, ChatTypeFilter
from app.core.bot.services.localization import Localization
from app.core.bot.services.logger import log
from app.core.bot.services.multi import handle_send, multi
from app.core.bot.services.requests.user.crud import manage_user
from app.core.bot.services.requests.user.state import manage_user_state
from app.core.database.models import User

router: Router = Router()


def user_callback(
    *filters: Any
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор для коллбеков в приватных чатах.

    Проверяет наличие сообщения, бота и локализации. Передает их в
    хэндлер через именованные аргументы tg_user, bot, loc, message.

    Args:
        *filters (Any): Дополнительные фильтры для callback_query.

    Returns:
        Callable: Обертка для функции-обработчика callback.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(
            callback: CallbackQuery,
            state: FSMContext,
            *args: Any,
            **kwargs: Any
        ) -> None:
            tg_user: Optional[TgUser] = callback.from_user
            message: Message | InaccessibleMessage | None = callback.message
            if message is None:
                return

            bot: Optional[Bot] = message.bot
            state_data: Dict[str, Any] = await state.get_data()
            loc: Optional[Localization] = state_data.get("loc_user")

            if tg_user is None or bot is None or loc is None:
                return

            kwargs.update({"tg_user": tg_user, "bot": bot,
                           "loc": loc, "message": message})
            return await func(callback, state, *args, **kwargs)

        return router.callback_query(
            ChatTypeFilter(
                ["private"]),
            *filters)(wrapper)

    return decorator


@user_callback(F.data == "delete")
async def clbk_delete(
    callback: CallbackQuery,
    state: FSMContext,
    *,
    tg_user: TgUser,
    bot: Bot,
    loc: Localization,
    message: Message
) -> None:
    """Удаляет сообщение в чате и логирует событие.

    Args:
        callback (CallbackQuery): Объект коллбека.
        state (FSMContext): Контекст FSM.
        tg_user (TgUser): Пользователь Telegram.
        bot (Bot): Экземпляр бота.
        loc (Localization): Локализация пользователя.
        message (Message): Сообщение для удаления.
    """
    await message.delete()
    await log(callback)


@user_callback(CallbackNextFilter())
async def clbk_next(
    callback: CallbackQuery,
    state: FSMContext,
    *,
    tg_user: TgUser,
    bot: Bot,
    loc: Localization,
    message: Message,
    value: Union[str, tuple[str, str, str]]
) -> None:
    """Обрабатывает callback кнопки next с формированием текста и клавиатуры.

    Args:
        callback (CallbackQuery): Объект коллбека.
        state (FSMContext): Контекст FSM.
        tg_user (TgUser): Пользователь Telegram.
        bot (Bot): Экземпляр бота.
        loc (Localization): Локализация пользователя.
        message (Message): Сообщение для редактирования.
        value (Union[str, tuple]): Данные для обработки.
    """
    data_select: Optional[list[str]] = None
    if isinstance(value, (list, tuple)) and len(value) == 3:
        data_select = [value[2], value[1]]
    text: str
    keyboard: InlineKeyboardMarkup
    text, keyboard = await multi(
        loc=loc,
        value=value[0] if isinstance(value, (list, tuple)) else value,
        tg_id=tg_user.id,
        data_select=data_select
    )

    try:
        await message.edit_text(text=text, reply_markup=keyboard)
        await manage_user_state(tg_user.id, "push", value[0])
    except BaseException:
        pass

    await log(callback)


@user_callback(F.data == "sending_data")
async def clbk_send(
    callback: CallbackQuery,
    state: FSMContext,
    *,
    tg_user: TgUser,
    bot: Bot,
    loc: Localization,
    message: Message
) -> None:
    """Отправляет данные пользователю и обновляет сообщение в БД.

    Args:
        callback (CallbackQuery): Объект коллбека.
        state (FSMContext): Контекст FSM.
        tg_user (TgUser): Пользователь Telegram.
        bot (Bot): Экземпляр бота.
        loc (Localization): Локализация пользователя.
        message (Message): Сообщение для редактирования.
    """
    msg_id: Optional[int] = await handle_send(
        loc=loc, tg_id=tg_user.id, event=callback
    )
    if not isinstance(msg_id, int):
        return

    try:
        msg_id_old: Union[int, User, bool, None] = await manage_user(
            tg_id=tg_user.id, action="msg_update", msg_id=msg_id
        )
        if isinstance(msg_id_old, int):
            await bot.delete_message(message.chat.id, msg_id_old)
        await manage_user_state(tg_user.id, "push", "100")
    except BaseException:
        pass

    await log(callback)


@user_callback(F.data == "userback")
async def clbk_back(
    callback: CallbackQuery,
    state: FSMContext,
    *,
    tg_user: TgUser,
    bot: Bot,
    loc: Localization,
    message: Message
) -> None:
    """Возврат на предыдущий шаг с формированием текста и клавиатуры.

    Args:
        callback (CallbackQuery): Объект коллбека.
        state (FSMContext): Контекст FSM.
        tg_user (TgUser): Пользователь Telegram.
        bot (Bot): Экземпляр бота.
        loc (Localization): Локализация пользователя.
        message (Message): Сообщение для редактирования.
    """
    backstate: Union[bool, str, list[str], None] = await manage_user_state(
        tg_user.id, "popeek"
    )
    if not isinstance(backstate, str):
        return
    
    text: str
    keyboard: InlineKeyboardMarkup
    text, keyboard = await multi(
        loc=loc, value=backstate, tg_id=tg_user.id
    )

    await callback.answer()

    try:
        await message.edit_text(text=text, reply_markup=keyboard)
    except BaseException:
        pass

    await log(callback)
