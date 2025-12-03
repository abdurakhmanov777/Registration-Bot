"""
Модуль обработки состояния выбора пользователя и формирования
сообщения и клавиатуры на основе локализации.
"""

from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions

from app.core.bot.services.keyboards.user import kb_select
from app.core.bot.services.multi.context import MultiContext
from app.core.bot.services.requests.data.crud import manage_data


async def handle_select(
    ctx: MultiContext,
) -> Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]:
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
    loc_state: Any = ctx.loc_state

    base_text: str = loc_state.text
    p1: str
    p2: str
    p1, p2 = loc.messages.template.select

    # Формирование сообщения
    text_message: str = f"{p1}{base_text}{p2}"

    # Формирование клавиатуры выбора
    keyboard: InlineKeyboardMarkup = kb_select(
        name=base_text,
        options=loc_state.options,
        buttons=loc.buttons
    )

    opts = LinkPreviewOptions(is_disabled=True)
    return text_message, keyboard, opts
