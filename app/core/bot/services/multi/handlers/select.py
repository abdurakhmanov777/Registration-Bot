"""
Модуль обработки состояния выбора пользователя и формирования
сообщения и клавиатуры на основе локализации.
"""

from typing import Tuple

from aiogram.types import InlineKeyboardMarkup

from app.core.bot.services.keyboards.user import kb_select
from app.core.bot.services.multi.context import MultiContext
from app.core.bot.services.requests.data.crud import manage_data


async def handle_select(
    ctx: MultiContext
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Обрабатывает состояние выбора пользователя и формирует сообщение
    и клавиатуру на основе шаблона локализации.

    Args:
        ctx (MultiContext): Контекст обработки шага.

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Текст сообщения и клавиатура.
    """

    loc = ctx.loc
    loc_state = ctx.loc_state
    tg_id = ctx.tg_id
    user_input = ctx.data  # выбранный пункт (если пользователь уже кликнул)

    base_text = loc_state.text
    p1, p2 = loc.template.select

    # Если пользователь сделал выбор — сохранить его
    if user_input is not None:
        await manage_data(
            tg_id=tg_id,
            action="create_or_update",
            key=base_text,
            value=user_input
        )

    # Сообщение
    text_message = f"{p1}{base_text}{p2}"

    # Клавиатура выбора
    keyboard_message: InlineKeyboardMarkup = kb_select(
        data=loc_state.keyboard,
        buttons=loc.button
    )

    return text_message, keyboard_message
