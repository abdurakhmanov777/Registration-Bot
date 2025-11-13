"""
Пакет requests для сервисов работы с запросами пользователей.

Включает подмодули user, data, работающие с БД.
"""

from .data import manage_data_crud, manage_data_list
from .user import manage_user, manage_user_state, manage_user_update

__all__: list[str] = [
    "manage_data_crud",
    "manage_data_list",
    "manage_user",
    "manage_user_state",
    "manage_user_update",
]
