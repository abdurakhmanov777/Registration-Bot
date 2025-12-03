"""
Модуль обработки текстового состояния пользователя и формирования
сообщения с клавиатурой на основе локализации.
"""

from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions

from app.core.bot.services.keyboards.user import kb_text
from app.core.bot.services.multi.context import MultiContext


async def handle_text(
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
    state_key: Any = loc_state.id  # Текущий ключ состояния (backstate)

    # Формируем текст сообщения
    text_message: str = loc_state.text

    # Формируем клавиатуру
    keyboard: InlineKeyboardMarkup = kb_text(
        state=loc_state.next,
        backstate=state_key,
        buttons=loc.buttons
    )
    # print(loc_state.link_disabled)
    opts = LinkPreviewOptions(
        is_disabled=not loc_state.link_preview
    )
    return text_message, keyboard, opts
