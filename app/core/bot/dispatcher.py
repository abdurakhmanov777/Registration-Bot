"""
Модуль для настройки диспетчера Telegram-бота и подключения
роутеров с соответствующими middleware.
"""

from typing import Any, Dict

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import SimpleEventIsolation

from app.core.bot.middleware import mw
from app.routers import (admin_callback, admin_command, admin_message,
                         user_callback, user_command, user_message)


async def _apply_middlewares(
    router_middleware_map: Dict[Any, Any]
) -> None:
    """
    Применяет middleware к соответствующим объектам роутеров.

    Args:
        router_middleware_map (Dict[Any, Any]): Словарь, где ключ —
            объект роутера (message или callback_query), а значение —
            экземпляр middleware.
    """
    for target, middleware in router_middleware_map.items():
        target.middleware(middleware)


async def setup_dispatcher() -> Dispatcher:
    """
    Асинхронная инициализация диспетчера и подключение роутеров
    с middleware.

    Returns:
        Dispatcher: Экземпляр диспетчера с подключенными
        роутерами и middleware.
    """
    # Создаем диспетчер с изоляцией событий в памяти
    dp: Dispatcher = Dispatcher(events_isolation=SimpleEventIsolation())

    # Применяем middleware к каждому роутеру
    await _apply_middlewares({
        admin_callback.callback_query: mw.MwAdminCallback(),
        admin_command.message: mw.MwAdminCommand(),
        admin_message.message: mw.MwAdminMessage(),
        user_callback.callback_query: mw.MwUserCallback(),
        user_command.message: mw.MwUserCommand(),
        user_message.message: mw.MwUserMessage(),
    })

    # Подключаем все роутеры к диспетчеру
    dp.include_routers(
        admin_callback,
        admin_command,
        admin_message,
        user_callback,
        user_command,
        user_message,
    )

    return dp
