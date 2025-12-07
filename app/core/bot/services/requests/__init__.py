"""
Пакет requests для сервисов работы с запросами пользователей.

Включает подмодули user, data, работающие с БД.
"""

from .data import manage_data, manage_data_list
from .user import manage_user_state

__all__: list[str] = [
    "manage_data",
    "manage_data_list",
    "manage_user_state",
]
