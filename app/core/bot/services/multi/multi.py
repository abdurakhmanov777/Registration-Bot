"""
Модуль маршрутизации генерации сообщений и клавиатур для пользователя
на основе локализации и текущего состояния.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

from aiogram import types

from app.core.bot.services.requests.data import manage_data

from .context import MultiContext
from .handlers.end import handle_end
from .handlers.input import handle_input
from .handlers.select import handle_select
from .handlers.start import handle_start
from .handlers.text import handle_text

HANDLERS: Dict[str, Callable[[MultiContext], Any]] = {
    "start": handle_start,
    "input": handle_input,
    "select": handle_select,
    "text": handle_text,
    "end": handle_end,
}


async def multi(
    loc: Any,
    value: str,
    tg_id: int,
    data: Optional[str] = None,
    data_select: Optional[List[str]] = None,
    event: Optional[Union[types.CallbackQuery, types.Message]] = None,
) -> Tuple[str, types.InlineKeyboardMarkup]:
    """Формирует текст сообщения и клавиатуру на основе состояния пользователя."""

    # Обработка специального состояния "1" без локализации
    if value == "1":
        loc_state: Optional[Any] = None
        handler: Callable[[MultiContext], Any] = handle_start

    else:
        loc_state = getattr(loc, f"userstate_{value}")

        # Pylance теперь знает, что loc_state точно не None
        loc_state_typed: Any = cast(Any, loc_state)

        handler_type: str = loc_state_typed.type
        handler = HANDLERS.get(handler_type, handle_start)

    context: MultiContext = MultiContext(
        loc=loc,
        loc_state=loc_state,
        value=value,
        tg_id=tg_id,
        data=data,
        event=event,
    )

    if data_select:
        key: str = data_select[0]
        value_to_store: str = data_select[1]

        await manage_data(
            tg_id=tg_id,
            action="create_or_update",
            key=key,
            value=value_to_store,
        )

    return await handler(context)
