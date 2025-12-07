"""
Модуль маршрутизации генерации сообщений и клавиатур пользователя
на основе локализации и текущего состояния.

Определяет функцию `multi`, которая выбирает соответствующий обработчик
шага, формирует контекст выполнения и возвращает параметры сообщения,
которые требуется отправить пользователю в Telegram.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from aiogram import types
from aiogram.fsm.context import FSMContext

from .context import MultiContext
from .handlers.input import handler_input
from .handlers.payment import handler_payment
from .handlers.select import handler_select
from .handlers.start import handler_start
from .handlers.submit import handler_submit
from .handlers.success import handler_success
from .handlers.text import handler_text

# Таблица стандартных обработчиков.
HANDLERS: Dict[str, Callable[[MultiContext], Any]] = {
    "input": handler_input,
    "select": handler_select,
    "text": handler_text,
}

# Таблица обработчиков для специальных состояний.
SPECIAL_HANDLERS: Dict[str, Callable[[MultiContext], Any]] = {
    "1": handler_start,
    "98": handler_submit,
    "99": handler_payment,
    "100": handler_success,
}


async def multi(
    state: FSMContext,
    value: str,
    tg_id: int,
    data: Optional[str] = None,
    data_select: Optional[List[str]] = None,
    event: Optional[Union[types.CallbackQuery, types.Message]] = None,
) -> Tuple[
    str,
    types.InlineKeyboardMarkup,
    types.LinkPreviewOptions
]:
    """
    Формирует параметры ответа Telegram в зависимости от состояния
    пользователя.

    Определяет, какой обработчик шага нужно вызвать, формирует контекст
    и возвращает текст, клавиатуру и параметры предпросмотра.

    Parameters
    ----------
    loc : Any
        Объект локализации текущего пользователя.
    value : str
        Текущее значение состояния.
    tg_id : int
        Telegram ID пользователя.
    data : Optional[str]
        Дополнительные данные, переданные пользователем.
    data_select : Optional[List[str]]
        Пара ключ–значение для сохранения в хранилище.
    event : Optional[Union[types.CallbackQuery, types.Message]]
        Telegram событие (сообщение или callback).

    Returns
    -------
    Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]
        Текст сообщения, клавиатура и параметры предпросмотра ссылок.
    """
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    # Определяем обработчик для специальных состояний, если они есть.
    handler: Optional[Callable[[MultiContext], Any]] = (
        SPECIAL_HANDLERS.get(value)
    )

    loc_state: Optional[Any] = None

    if handler is None:
        # Если состояние не специальное, определяем его по локализации.
        loc_state = getattr(loc.steps, value, None)

        # Если состояние локализации не найдено, используем стартовый
        # обработчик, чтобы избежать зависания пользователя.
        handler = (
            HANDLERS.get(loc_state.type, handler_start)
            if loc_state
            else handler_start
        )

    context = MultiContext(
        state=state,
        loc=loc,
        loc_state=loc_state,
        value=value,
        tg_id=tg_id,
        data=data,
        event=event,
    )

    # Сохраняем выбранные пользователем данные заранее, так как они могут
    # влиять на поведение последующих шагов.
    if data_select:
        key: str
        value_to_store: str
        key, value_to_store = data_select[:2]
        user_data: Dict[str, Any] = await state.get_data()
        data_db: Any = user_data.get("data_db")
        data_db[key] = value_to_store

    return await handler(context)
