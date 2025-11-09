"""
Алиасы для создания middleware:
- MwCommand для command,
- MwMessage для message,
- MwCallback для callback_query.
"""

from typing import Any

from .base import MwBase


def MwAdminCallback(**extra_data: Any) -> MwBase:
    """Middleware для callback query админов."""
    return MwBase(delete_event=False, role="admin", **extra_data)


def MwAdminCommand(**extra_data: Any) -> MwBase:
    """Middleware для команд админов с админской локализацией."""
    return MwBase(delete_event=True, role="admin", **extra_data)


def MwAdminMessage(**extra_data: Any) -> MwBase:
    """Middleware для сообщений админов."""
    return MwBase(delete_event=True, role="admin", **extra_data)


def MwUserCallback(**extra_data: Any) -> MwBase:
    """Middleware для callback query юзеров."""
    return MwBase(delete_event=False, role="user", **extra_data)


def MwUserCommand(**extra_data: Any) -> MwBase:
    """Middleware для команд юзеров."""
    return MwBase(delete_event=True, role="user", **extra_data)


def MwUserMessage(**extra_data: Any) -> MwBase:
    """Middleware для сообщений юзеров."""
    return MwBase(delete_event=True, role="user", **extra_data)
