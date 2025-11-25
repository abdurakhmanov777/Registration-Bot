"""
Модуль обработки состояния стартового сообщения пользователя
и формирования клавиатуры на основе локализации.
"""

from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup

from app.bot.services.keyboards.user import kb_start


async def handle_start(
    loc: Any,
    loc_state: Any,
    value: str,
    tg_id: int,
    data: str | None
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Обрабатывает стартовое состояние пользователя и формирует
    сообщение и клавиатуру на основе шаблона локализации.

    Args:
        loc (Any): Объект локализации с шаблонами сообщений.
        loc_state (Any): Состояние пользователя для обработки.
        value (str): Ключ текущего состояния пользователя.
        tg_id (int): Telegram ID пользователя.
        data (str | None): Данные пользователя (не используется).

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Текст сообщения и объект
        клавиатуры для ответа пользователю.
    """
    # Формируем текст стартового сообщения на основе шаблона
    p1: Any
    p2: Any
    p1, p2 = loc.template.start
    text_message: str = f"{p1}{loc_state.text}{p2}"

    # Создаём стартовую клавиатуру
    keyboard_message: InlineKeyboardMarkup = kb_start(
        buttons=loc.button
    )

    return text_message, keyboard_message
