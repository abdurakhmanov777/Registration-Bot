from aiogram import Dispatcher
from aiogram.fsm.storage.memory import SimpleEventIsolation

from app.middlewares.middlewares import MwCallback, MwCommand
from app.routers.admin.callback import router as admin_callback
from app.routers.admin.command import router as admin_command
from app.routers.user.callback import router as user_callback
from app.routers.user.command import router as user_command


def _apply_middlewares(
    router_middleware_map: dict
) -> None:
    """
    Применяет указанные middlewares к соответствующим объектам роутеров.

    Args:
        router_middleware_map (dict): Словарь,
            где ключ — целевой объект (message или callback_query),
            значение — экземпляр middleware.
    """
    for target, middleware in router_middleware_map.items():
        target.middleware(middleware)


def init_routers() -> Dispatcher:
    """
    Инициализация диспетчера и подключение роутеров с middlewares.

    Returns:
        Dispatcher: Экземпляр диспетчера с подключенными
        роутерами и middlewares.
    """
    dp = Dispatcher(events_isolation=SimpleEventIsolation())

    _apply_middlewares({
        admin_callback.callback_query: MwCallback(),
        admin_command.message: MwCommand(),
        user_callback.callback_query: MwCallback(),
        user_command.message: MwCommand(),
    })

    dp.include_routers(
        admin_command,
        admin_callback,
        user_command,
        user_callback,
    )

    return dp
