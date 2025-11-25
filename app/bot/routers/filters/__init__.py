"""
Инициализация модуля фильтров.

Импортирует все доступные фильтры для упрощения их использования
в роутерах и других модулях приложения.
"""

# Импорт фильтров
from .admin import AdminFilter
from .chat_type import ChatTypeFilter
from .intercept import InterceptFilter
from .user import CallbackFilterNext

# Экспортируемые объекты модуля
__all__: list[str] = [
    "AdminFilter",
    "ChatTypeFilter",
    "InterceptFilter",
    "CallbackFilterNext",
]
