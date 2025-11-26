"""
Модуль обработки состояния ввода пользователя и формирования
сообщения и клавиатуры на основе локализации.
"""

import re
from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup

from app.core.bot.services.keyboards.user import kb_input
from app.core.bot.services.multi.context import MultiContext
from app.core.bot.services.requests.data.crud import manage_data
from app.core.bot.utils.morphology.casing import lower_words
from app.core.bot.utils.morphology.inflection import inflect_text


async def handle_input(
    ctx: MultiContext
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Обрабатывает состояние ввода пользователя и формирует сообщение
    и клавиатуру на основе шаблона локализации.

    Args:
        ctx (MultiContext): Контекст обработки шага.

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Текст сообщения и клавиатура.
    """

    loc = ctx.loc
    loc_state = ctx.loc_state
    tg_id = ctx.tg_id
    data = ctx.data

    format_ = loc_state.format
    pattern = loc_state.pattern
    base_text = loc_state.text
    template = loc.template.input

    error = False

    # Проверка пользовательского ввода по regex
    if data is not None:
        regex = re.compile(pattern)
        if regex.fullmatch(data):
            data = await manage_data(
                tg_id=tg_id,
                action="create_or_update",
                key=base_text,
                value=data
            )
        else:
            error = True
    else:
        # Если пользователь ничего не ввёл — получить ранее сохранённые данные
        data = await manage_data(
            tg_id=tg_id,
            action="get",
            key=base_text
        )

    # Формирование текста сообщения
    if error:
        p1, p2 = template.error
        text_message = f"{p1}{format_}{p2}"

        show_next = False

    elif not data:
        # пустое значение → склонение шаблона
        p1, p2, p3 = template.empty

        processed_text = await inflect_text(
            text=await lower_words(base_text, capitalize_first=False),
            case="винительный"
        )

        text_message = f"{p1}{processed_text}{p2}{format_}{p3}"

        show_next = False

    else:
        # поле заполнено
        p1, p2, p3 = template.filled
        text_message = f"{p1}{base_text}{p2}{data}{p3}"

        show_next = True

    # Клавиатура
    keyboard_message: InlineKeyboardMarkup = kb_input(
        state=loc_state.keyboard,
        backstate=ctx.value,
        show_next=show_next,
        buttons=loc.button
    )

    return text_message, keyboard_message
