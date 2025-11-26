"""
Модуль маршрутизации формирования сообщений и клавиатур
для пользователя на основе локализации и состояния.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class MultiContext:
    """
    Контекст, содержащий параметры для обработки состояния пользователя.
    """

    loc: Any
    loc_state: Any
    value: str
    tg_id: int
    data: str | None = None
    extra: Dict[str, Any] | None = None
