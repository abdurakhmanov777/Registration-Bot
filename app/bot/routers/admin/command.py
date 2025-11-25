from typing import Any, Callable

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.bot.routers.filters import AdminFilter, ChatTypeFilter
from app.bot.services.keyboards import keyboard_dynamic
from app.bot.services.logger import log

router: Router = Router()


def admin_command(
    *filters: Any
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Декоратор для регистрации команд, доступных только
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


@admin_command(Command("admin"))
async def start(
    message: Message,
    state: FSMContext,
    role: str
) -> None:
    """
    Отправляет текст и динамическую клавиатуру из локализации
    для администратора.

    Args:
        message (Message): Объект входящего сообщения Telegram.
        state (FSMContext): Контекст FSM для хранения данных.
        role (str): Роль пользователя для логирования или
        фильтрации.
    """

    # Получаем данные локализации из состояния
    data: dict = await state.get_data()
    loc: Any | None = data.get("loc_admin")
    if not loc:
        return

    # Получаем текст и данные клавиатуры из локализации
    text: str = loc.default.admin.text
    keyboard_data: list = loc.default.admin.keyboard

    # Создаём динамическую клавиатуру
    keyboard: InlineKeyboardMarkup = await keyboard_dynamic(keyboard_data)

    # Отправляем сообщение с текстом и клавиатурой
    await message.answer(
        text=text,
        reply_markup=keyboard
    )

    await log(message)
