"""
Пакет менеджеров базы данных.

Импортирует все менеджеры для работы с моделями
"""

from .admin import AdminManager
# from .data import DataManager
from .flag import FlagManager
from .user import UserManager

# from .user import User

# Список публичных объектов модуля
__all__: list[str] = [
    "AdminManager",
    # "DataManager",
    "FlagManager",
    "UserManager",
]
