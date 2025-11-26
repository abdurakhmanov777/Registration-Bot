"""
Модуль обработки стартового состояния пользователя
и формирования клавиатуры на основе локализации.
"""

from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup

from app.core.bot.services.keyboards.user import kb_start
from app.core.bot.services.multi.context import MultiContext


async def handle_start(
    ctx: MultiContext,
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Обрабатывает стартовое состояние пользователя и формирует сообщение
    и клавиатуру на основе локализации.

    Args:
        ctx (MultiContext): Контекст мульти-обработчика, содержащий update/event,
                            loc, loc_state, value, tg_id, data и extra.

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Текст сообщения и объект клавиатуры.
    """

    loc = ctx.loc
    loc_state = ctx.loc_state

    # Формируем текст сообщения
    prefix, suffix = loc.template.start
    text_message: str = f"{prefix}{loc_state.text}{suffix}"

    # Формируем клавиатуру
    keyboard: InlineKeyboardMarkup = kb_start(buttons=loc.button)

    return text_message, keyboard
