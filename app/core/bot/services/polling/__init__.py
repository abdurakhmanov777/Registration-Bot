"""
Пакет для управления опросом Telegram-ботов.

Содержит:
- PollingManager — класс менеджера опроса.
- get_polling_manager — функция для получения глобального экземпляра менеджера.
"""

from .instance import get_polling_manager
from .manager import PollingManager

__all__: list[str] = [
    "get_polling_manager",
    "PollingManager",
]
