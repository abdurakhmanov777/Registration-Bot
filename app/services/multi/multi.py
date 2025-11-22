"""
Модуль маршрутизации формирования сообщений и клавиатур
для пользователя на основе локализации и состояния.
"""

from typing import Any, Callable, Tuple

from aiogram.types import InlineKeyboardMarkup

from app.services.multi.handlers.end import handle_end

from .handlers.input import handle_input
from .handlers.select import handle_select
from .handlers.start import handle_start
from .handlers.text import handle_text


async def multi(
    loc: Any,
    value: str,
    tg_id: int,
    data: str | None = None
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Формирует текст сообщения и клавиатуру для пользователя
    в зависимости от типа состояния.

    Args:
        loc (Any): Объект локализации с состояниями пользователя.
        value (str): Ключ текущего состояния пользователя.
        tg_id (int): Telegram ID пользователя.
        data (str | None, optional): Данные, введённые пользователем.
            По умолчанию None.

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Текст сообщения и объект
        клавиатуры для ответа пользователю.
    """
    loc_state: Any = getattr(loc, f"userstate_{value}")
    type_message: str = loc_state.type

    # Словарь, сопоставляющий тип состояния с обработчиком
    handler_map: dict[str, Callable[..., Any]] = {
        "input": handle_input,
        "select": handle_select,
        "text": handle_text,
        "start": handle_start,
        "end": handle_end
    }

    # Выбираем обработчик по типу состояния, по умолчанию start
    handler: Callable[..., Any] = handler_map.get(type_message, handle_start)

    return await handler(
        loc=loc,
        loc_state=loc_state,
        value=value,
        tg_id=tg_id,
        data=data
    )
