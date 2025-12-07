"""
Модуль обработки текстового состояния пользователя и формирования
сообщения с клавиатурой на основе локализации.

Подготавливает текст сообщения и генерирует подходящую клавиатуру
в зависимости от текущего состояния локализации.
"""

from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions

from app.core.bot.services.keyboards.user import kb_dynamic

from ..context import MultiContext


async def handler_text(
    ctx: MultiContext,
) -> Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]:
    """
    Обрабатывает текстовое состояние пользователя.

    Формирует текст сообщения и инлайн-клавиатуру на основе текущего
    локализованного состояния, а также параметры предпросмотра ссылок.

    Parameters
    ----------
    ctx : MultiContext
        Контекст, содержащий данные пользователя, локализацию и
        состояние текущего шага.

    Returns
    -------
    Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]
        Кортеж, содержащий текст сообщения, клавиатуру и параметры
        предпросмотра ссылок.
    """
    loc: Any = ctx.loc
    loc_state: Any = ctx.loc_state

    # Ключ состояния используется для формирования кнопки "Назад"
    state_key: Any = loc_state.id

    # Текст сообщения полностью определяется локалью состояния
    text_message: str = loc_state.text

    # Формирование клавиатуры на основе следующего состояния
    keyboard: InlineKeyboardMarkup = kb_dynamic(
        buttons=loc.buttons,
        state=loc_state.next,
        backstate=state_key,
    )

    # Управление предпросмотром ссылок в сообщении
    preview_options = LinkPreviewOptions(
        is_disabled=not loc_state.link_preview
    )

    return text_message, keyboard, preview_options
