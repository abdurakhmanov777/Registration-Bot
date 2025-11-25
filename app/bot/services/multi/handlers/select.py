"""
Модуль обработки состояния выбора пользователя и формирования
сообщения с клавиатурой на основе локализации.
"""

from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup

from app.bot.services.keyboards.user import kb_select


async def handle_select(
    loc: Any,
    loc_state: Any,
    value: str,
    tg_id: int,
    data: str | None
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Обрабатывает состояние выбора пользователя и формирует сообщение
    и клавиатуру на основе шаблона локализации.

    Args:
        loc (Any): Объект локализации с шаблонами сообщений.
        loc_state (Any): Состояние пользователя для обработки.
        value (str): Ключ текущего состояния пользователя.
        tg_id (int): Telegram ID пользователя.
        data (str | None): Данные, введённые пользователем (не используется).

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Текст сообщения и объект
        клавиатуры для ответа пользователю.
    """
    # Формируем текст сообщения на основе шаблона select
    p1: Any
    p2: Any
    p1, p2 = loc.template.select
    text_message: str = f"{p1}{loc_state.text}{p2}"

    # Создаём клавиатуру выбора на основе данных состояния
    keyboard_message: InlineKeyboardMarkup = kb_select(
        data=loc_state.keyboard,
        buttons=loc.button
    )

    return text_message, keyboard_message
