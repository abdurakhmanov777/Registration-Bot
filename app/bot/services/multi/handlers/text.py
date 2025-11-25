"""
Модуль обработки текстового состояния пользователя и формирования
сообщения с клавиатурой на основе локализации.
"""

from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup

from app.bot.services.keyboards.user import kb_text


async def handle_text(
    loc: Any,
    loc_state: Any,
    value: str,
    tg_id: int,
    data: str | None
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Обрабатывает текстовое состояние пользователя и формирует
    сообщение и клавиатуру на основе шаблона локализации.

    Args:
        loc (Any): Объект локализации с шаблонами сообщений.
        loc_state (Any): Состояние пользователя для обработки.
        value (str): Ключ текущего состояния пользователя.
        tg_id (int): Telegram ID пользователя.
        data (str | None): Данные пользователя (не используются).

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Текст сообщения и объект
        клавиатуры для ответа пользователю.
    """
    # Используем текст из состояния напрямую
    text_message: str = loc_state.text

    # Создаём клавиатуру для текстового состояния
    keyboard_message: InlineKeyboardMarkup = kb_text(
        state=loc_state.keyboard,
        backstate=value,
        buttons=loc.button
    )

    return text_message, keyboard_message
