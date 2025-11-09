from typing import Any, Callable

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.config import COMMAND_MAIN
from app.filters import ChatTypeFilter
from app.services.keyboards import keyboard_dynamic
from app.services.logger import log

router = Router()


def user_message() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
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
        )(func)
    return decorator


@user_message()
async def user_id(
    message: Message,
    state: FSMContext
) -> None:
    pass
