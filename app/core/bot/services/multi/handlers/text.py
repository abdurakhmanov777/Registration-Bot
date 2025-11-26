"""
Модуль обработки текстового состояния пользователя и формирования
сообщения с клавиатурой на основе локализации.
"""

from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup

from app.core.bot.services.keyboards.user import kb_text
from app.core.bot.services.multi.context import MultiContext


async def handle_text(
    ctx: MultiContext,
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Обрабатывает текстовое состояние пользователя и формирует сообщение
    и клавиатуру согласно шаблонам локализации.

    Args:
        ctx (MultiContext): Контекст мульти-обработчика, содержащий
                            update/event, loc, loc_state, value, tg_id, data и extra.

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Текст сообщения и объект клавиатуры.
    """

    loc = ctx.loc
    loc_state = ctx.loc_state
    state_key = ctx.value  # текущий ключ состояния, используется как backstate

    # Формируем текст сообщения (только текст из состояния)
    text_message: str = loc_state.text

    # Формируем клавиатуру
    keyboard: InlineKeyboardMarkup = kb_text(
        state=loc_state.keyboard,
        backstate=state_key,
        buttons=loc.button
    )

    return text_message, keyboard
