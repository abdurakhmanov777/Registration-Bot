"""
Инициализация всех менеджеров базы данных.

Модуль предоставляет единый доступ ко всем менеджерам, обеспечивая
CRUD и вспомогательные операции для работы с таблицами:
Admin, Data, Flag и User.
"""

from .admin import AdminManager
from .data import DataManager
from .flag import FlagManager
from .user import UserManager

# Список менеджеров, доступных для импорта через '*'
__all__: list[str] = [
    "AdminManager",
    "DataManager",
    "FlagManager",
    "UserManager",
]
