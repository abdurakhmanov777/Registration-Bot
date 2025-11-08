"""
Алиасы для создания middleware:
- MwCommand для команд,
- MwMessage для сообщений,
- MwCallback для callback query.
"""

from typing import Any

from .base import MwBase


def MwCommand(**extra_data: Any) -> MwBase:
    """
    Middleware для команд.

    Удаляет событие после обработки.
    """
    return MwBase(delete_event=True, **extra_data)


def MwMessage(**extra_data: Any) -> MwBase:
    """
    Middleware для сообщений.

    Удаляет событие после обработки.
    """
    return MwBase(delete_event=True, **extra_data)


def MwCallback(**extra_data: Any) -> MwBase:
    """
    Middleware для callback query.

    Не удаляет событие после обработки.
    """
    return MwBase(delete_event=False, **extra_data)
