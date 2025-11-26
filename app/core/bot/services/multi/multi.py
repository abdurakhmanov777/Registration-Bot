"""
Модуль маршрутизации формирования сообщений и клавиатур
для пользователя на основе локализации и состояния.
"""

from typing import Any, Callable, Tuple

from aiogram import types

from app.core.bot.services.requests.data import manage_data

from .context import MultiContext
from .handlers.end import handle_end
from .handlers.input import handle_input
from .handlers.select import handle_select
# from .handlers.send import handle_send
from .handlers.start import handle_start
from .handlers.text import handle_text


async def multi(
    loc: Any,
    value: str,
    tg_id: int,
    data: str | None = None,
    data_select: list[str] | None = None,
    event: types.CallbackQuery | types.Message | None = None,
    **extra: Any
) -> Tuple[str, types.InlineKeyboardMarkup]:
    """
    Формирует текст сообщения и клавиатуру для пользователя
    в зависимости от типа состояния.

    Args:
        loc (Any): Объект локализации.
        value (str): Ключ состояния пользователя.
        tg_id (int): Telegram ID пользователя.
        data (str | None): Данные, введённые пользователем.
        extra (dict): Дополнительные параметры.

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Текст сообщения и клавиатура.
    """

    loc_state: Any = getattr(loc, f"userstate_{value}")
    type_message: str = loc_state.type

    context = MultiContext(
        loc=loc,
        loc_state=loc_state,
        value=value,
        tg_id=tg_id,
        data=data,
        event=event,
        extra=extra or {},
    )

    handler_map: dict[str, Callable[[MultiContext], Any]] = {
        "input": handle_input,
        "select": handle_select,
        "text": handle_text,
        "start": handle_start,
        "end": handle_end,
    }

    handler: Callable[[MultiContext], Any] = handler_map.get(
        type_message,
        handle_start
    )

    if data_select:
        await manage_data(
            tg_id=tg_id,
            action="create_or_update",
            key=data_select[0],
            value=data_select[1]
        )

    return await handler(context)
