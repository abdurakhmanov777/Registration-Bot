"""
Модуль обработки финального состояния пользователя,
формирования итогового сообщения и клавиатуры.
"""

from typing import Any, Dict, Tuple

from aiogram.types import InlineKeyboardMarkup

from app.core.bot.services.keyboards.user import kb_end
from app.core.bot.services.multi.context import MultiContext
from app.core.bot.services.requests.data.dlist import manage_data_list


async def handle_end(
    ctx: MultiContext
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Обрабатывает финальное состояние пользователя и формирует сообщение.

    Формирует текст на основе шаблона локализации и списка данных,
    собранных от пользователя.

    Args:
        ctx (MultiContext): Контекст с параметрами обработки.

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Итоговое сообщение и клавиатура.
    """

    # Получаем список всех данных пользователя
    data_list: Dict[str, Any] = await manage_data_list(tg_id=ctx.tg_id)

    # Формируем текст блоков данных
    items: str = "\n\n".join(
        f"🔹️ {key}: {val}" for key, val in data_list.items()
    )

    # Шаблон локализации (начало и конец)
    prefix, suffix = ctx.loc.template.end

    text_message: str = f"{prefix}{items}{suffix}"

    # Клавиатура завершения
    keyboard_message: InlineKeyboardMarkup = kb_end(
        buttons=ctx.loc.button
    )

    return text_message, keyboard_message
