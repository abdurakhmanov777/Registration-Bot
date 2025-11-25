"""
Пакет для работы с таблицами пользователей и пользовательских данных.

Содержит:
    - CRUD-классы для работы с таблицами User и Data;
    - Универсальные асинхронные обёртки для основных операций.
"""

from .crud import manage_data
from .dlist import manage_data_clear, manage_data_list

__all__: list[str] = [
    "manage_data",
    "manage_data_clear",
    "manage_data_list",
]
