"""
Алиасы для создания middleware.

Доступные алиасы:
    - MwAdminCallback для admin callback query
    - MwAdminCommand для admin команд
    - MwAdminMessage для admin сообщений
    - MwSystemBlock для системной блокировки
    - MwUserCallback для пользовательских callback query
    - MwUserCommand для пользовательских команд
    - MwUserMessage для пользовательских сообщений
"""

from typing import Any

from .base import MwBase


def MwAdminCallback(
    **extra_data: Any,
) -> MwBase:
    """
    Middleware для callback query админов.

    Args:
        **extra_data: Дополнительные параметры для MwBase.

    Returns:
        MwBase: Экземпляр middleware для админского callback.
    """
    return MwBase(
        delete_event=False,
        role="admin",
        **extra_data,
    )


def MwAdminCommand(
    **extra_data: Any,
) -> MwBase:
    """
    Middleware для команд админов с админской локализацией.

    Args:
        **extra_data: Дополнительные параметры для MwBase.

    Returns:
        MwBase: Экземпляр middleware для админской команды.
    """
    return MwBase(
        delete_event=True,
        role="admin",
        **extra_data,
    )


def MwAdminMessage(
    **extra_data: Any,
) -> MwBase:
    """
    Middleware для сообщений админов.

    Args:
        **extra_data: Дополнительные параметры для MwBase.

    Returns:
        MwBase: Экземпляр middleware для админского сообщения.
    """
    return MwBase(
        delete_event=True,
        role="admin",
        **extra_data,
    )


def MwSystemBlock(
    **extra_data: Any,
) -> MwBase:
    """
    Middleware для перехвата сообщений и callback при системной
    блокировке бота.

    Args:
        **extra_data: Дополнительные параметры для MwBase.

    Returns:
        MwBase: Экземпляр middleware для системной блокировки.
    """
    return MwBase(
        delete_event=True,
        role="user",
        **extra_data,
    )


def MwUserCallback(
    **extra_data: Any,
) -> MwBase:
    """
    Middleware для callback query обычных пользователей.

    Args:
        **extra_data: Дополнительные параметры для MwBase.

    Returns:
        MwBase: Экземпляр middleware для пользовательского callback.
    """
    return MwBase(
        delete_event=False,
        role="user",
        **extra_data,
    )


def MwUserCommand(
    **extra_data: Any,
) -> MwBase:
    """
    Middleware для команд обычных пользователей.

    Args:
        **extra_data: Дополнительные параметры для MwBase.

    Returns:
        MwBase: Экземпляр middleware для пользовательской команды.
    """
    return MwBase(
        delete_event=True,
        role="user",
        **extra_data,
    )


def MwUserMessage(
    **extra_data: Any,
) -> MwBase:
    """
    Middleware для сообщений обычных пользователей.

    Args:
        **extra_data: Дополнительные параметры для MwBase.

    Returns:
        MwBase: Экземпляр middleware для пользовательского сообщения.
    """
    return MwBase(
        delete_event=True,
        role="user",
        **extra_data,
    )
