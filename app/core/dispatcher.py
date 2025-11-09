"""
Создание диспетчера и подключение роутеров с middlewares.
"""

from typing import Any, Dict

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import SimpleEventIsolation

from app.core.middleware import mw
from app.routers import (admin_callback, admin_command, admin_message,
                         user_callback, user_command, user_message)


async def _apply_middlewares(router_middleware_map: Dict[Any, Any]) -> None:
    """
    Применяет указанные middlewares к соответствующим объектам роутеров.

    Args:
        router_middleware_map (Dict[Any, Any]): Словарь,
            где ключ — объект (message или callback_query),
            значение — экземпляр middleware.
    """
    for target, middleware in router_middleware_map.items():
        target.middleware(middleware)


async def setup_dispatcher() -> Dispatcher:
    """
    Асинхронная инициализация диспетчера и подключение роутеров
    с middlewares.

    Returns:
        Dispatcher: Экземпляр диспетчера с подключенными
        роутерами и middlewares.
    """
    dp = Dispatcher(events_isolation=SimpleEventIsolation())

    await _apply_middlewares({
        admin_callback.callback_query: mw.MwAdminCallback(),
        admin_command.message: mw.MwAdminCommand(),
        admin_message.message: mw.MwAdminMessage(),
        user_callback.callback_query: mw.MwUserCallback(),
        user_command.message: mw.MwUserCommand(),
        user_message.message: mw.MwUserMessage(),
    })

    dp.include_routers(
        admin_callback,
        admin_command,
        admin_message,
        user_callback,
        user_command,
        user_message,
    )

    return dp
