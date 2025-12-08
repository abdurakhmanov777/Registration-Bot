"""Модуль, содержащий класс контекста для обработки состояния пользователя в боте."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aiogram import types
from aiogram.fsm.context import FSMContext


@dataclass(slots=True)
class MultiContext:
    """Контекст, содержащий параметры для обработки состояния пользователя.

    Атрибуты:
        loc (Any): Объект локализации, содержащий состояния пользователя.
        loc_state (Any): Конкретное состояние пользователя.
        value (str): Идентификатор текущего состояния.
        tg_id (int): Telegram ID пользователя.
        data (Optional[str]): Дополнительные данные, переданные пользователем.
        event (Optional[Union[types.CallbackQuery, types.Message]]):
            Событие Telegram, которое вызвало этот контекст.
    """
    state: FSMContext
    loc: Any
    loc_state: Any
    value: str = ""
    tg_id: int = 0
    data: Optional[str] = None
    event: Optional[types.CallbackQuery | types.Message] = None
