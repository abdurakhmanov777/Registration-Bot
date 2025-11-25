from typing import Any, Callable, Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.bot.routers.filters import AdminFilter, ChatTypeFilter
from app.bot.services.keyboards import keyboard_dynamic
from app.bot.services.logger import log
from app.config import COMMAND_MAIN

router: Router = Router()


def admin_message(
    *filters: Any
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Декоратор для регистрации сообщений, доступных только
    администраторам в приватных чатах.

    Args:
        *filters (Any): Дополнительные фильтры для обработки
        сообщений.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]:
        Декоратор для функции-обработчика.
    """
    def decorator(
        func: Callable[..., Any]
    ) -> Callable[..., Any]:
        return router.message(
            ChatTypeFilter(chat_type=["private"]),
            AdminFilter(),
            *filters
        )(func)

    return decorator
