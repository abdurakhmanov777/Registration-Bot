from typing import Any, Callable, Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.config import COMMAND_MAIN
from app.filters import AdminFilter, ChatTypeFilter
from app.services.keyboards import keyboard_dynamic
from app.services.logger import log

router = Router()


def admin_command(
    *commands: str
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Декоратор для регистрации команд, доступных только
        в группах и супергруппах.

    Args:
        *commands (str): Названия команд для
        фильтрации (например, "start", "help").

    Returns:
        Callable: Декоратор для функции-обработчика.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return router.message(
            ChatTypeFilter(chat_type=["private"]),
            AdminFilter(),
            Command(*commands)
        )(func)
    return decorator
