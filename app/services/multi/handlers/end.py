"""
Модуль обработки состояния стартового сообщения пользователя
и формирования клавиатуры на основе локализации.
"""

from typing import Any, Dict, Tuple

from aiogram.types import InlineKeyboardMarkup

from app.core.database.models.data import Data
from app.services.keyboards.user import kb_end
from app.services.requests.data.dlist import manage_data_list


async def handle_end(
    loc: Any,
    loc_state: Any,
    value: str,
    tg_id: int,
    data: str | None
) -> Tuple[str, InlineKeyboardMarkup]:
    """Обрабатывает стартовое состояние пользователя и формирует сообщение.

    Формирует текст сообщения и клавиатуру на основе шаблона локализации
    и данных пользователя.

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
    # Получаем список всех данных пользователя
    data_list: Dict[str, Any] = await manage_data_list(tg_id=tg_id)

    # Формируем строку с элементами данных
    items: str = '\n\n'.join(
        f'🔹️ {key}: {str(val)}' for key, val in data_list.items()
    )

    # Разбираем шаблон локализации на префикс и суффикс
    p1: Any
    p2: Any
    p1, p2 = loc.template.end

    # Формируем итоговый текст сообщения
    text_message: str = f"{p1}{items}{p2}"

    # Создаем клавиатуру завершения
    keyboard_message: InlineKeyboardMarkup = kb_end()

    return text_message, keyboard_message
