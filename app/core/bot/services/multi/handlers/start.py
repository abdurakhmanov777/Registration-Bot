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
    Обрабатывает состояние пользователя и формирует сообщение.

    Формирует текст на основе шаблона локализации и списка данных,
    собранных от пользователя.

    Args:
        ctx (MultiContext): Контекст с параметрами обработки.

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Сообщение и клавиатура.
    """

    loc: Any = ctx.loc

    # Формируем текст сообщения
    p1: str
    p2: str
    p1, p2 = loc.template.start
    text_message: str = f"{p1}{loc.info.name}{p2}"

    # Формируем клавиатуру
    keyboard: InlineKeyboardMarkup = kb_start(buttons=loc.button)

    return text_message, keyboard
