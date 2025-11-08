from typing import Any, Callable

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.core.config import COMMAND_MAIN
from app.filters import AdminFilter, ChatTypeFilter
from app.services.keyboards import keyboard_dynamic
from app.utils.logger import log

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


@admin_command("admin")
async def admin_start(
    message: Message,
    state: FSMContext,
    admin_role: dict
) -> None:
    """
    Отправляет ID текущего группового чата с шаблоном текста
        и динамической клавиатурой.

    Args:
        message (Message): Объект входящего сообщения Telegram.
        state (FSMContext): Объект контекста состояний FSM.
    """
    # Формируем текст и отправляем сообщение
    text: str = f"Админ панель\n\n{admin_role['role']}"
    await message.answer(text=text, parse_mode="HTML")
    await log(message)
