"""
Алиасы для создания middleware.

Доступные алиасы:
    - MwAdminCallback для admin callback_query
    - MwAdminMessage для admin сообщений
    - MwSystemBlock для системной блокировки
    - MwUserCallback для пользовательских callback_query
    - MwUserMessage для пользовательских сообщений
"""

from typing import Any

from aiogram.types import ContentType

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


def MwUserCallback() -> MwBase:
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
    )


def MwUserMessage() -> MwBase:
    """
    Middleware для сообщений пользователей.

    Returns:
        MwBase: Экземпляр middleware для пользовательского сообщения.
    """
    return MwBase(
        delete_event=True,
        role="user",
    )


def MwUserPayment() -> MwBase:
    """
    Middleware для оплаты.

    Returns:
        MwBase: Экземпляр middleware для пользовательского сообщения.
    """
    return MwBase(
        delete_event=True,
        role="user",
        allowed_types={
            ContentType.TEXT,               # обычные текстовые сообщения
            ContentType.SUCCESSFUL_PAYMENT  # успешные платежи
        }
    )
