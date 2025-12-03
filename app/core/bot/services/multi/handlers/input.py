"""
Модуль обработки состояния ввода пользователя и формирования
сообщения и клавиатуры на основе локализации.
"""

import re
from typing import Any, Dict, Optional, Tuple

from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions

from app.core.bot.services.keyboards.user import kb_input
from app.core.bot.services.multi.context import MultiContext
from app.core.bot.services.requests.data.crud import manage_data
from app.core.bot.utils.morphology.casing import lower_words
from app.core.bot.utils.morphology.inflection import inflect_text


async def handle_input(
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
    tg_id: int = ctx.tg_id
    user_input: Optional[str] = ctx.data

    format_: str = loc_state.format
    pattern: str = loc_state.pattern
    base_text: str = loc_state.text
    template: Any = loc.messages.template.input

    error_occurred: bool = False
    text_message: str
    show_next: bool
    p1: str
    p2: str
    p3: str
    # Проверка пользовательского ввода по регулярному выражению
    if user_input is not None:
        if re.fullmatch(pattern, user_input):
            await manage_data(
                tg_id=tg_id,
                action="create_or_update",
                key=base_text,
                value=user_input
            )
        else:
            error_occurred = True
    else:
        # Получаем ранее сохранённые данные, если пользователь ничего не ввёл
        user_input = await manage_data(
            tg_id=tg_id,
            action="get",
            key=base_text
        )

    # Формирование текста сообщения
    if error_occurred:
        p1, p2 = template.error
        text_message = f"{p1}{format_}{p2}"
        show_next = False

    elif not user_input:
        # Пустое значение → склонение шаблона
        p1, p2, p3 = template.empty

        processed_text: str = await inflect_text(
            text=await lower_words(base_text, capitalize_first=False),
            case="винительный"
        )
        text_message = f"{p1}{processed_text}{p2}{format_}{p3}"
        show_next = False

    else:
        # Поле заполнено
        p1, p2, p3 = template.filled
        text_message = f"{p1}{base_text}{p2}{user_input}{p3}"
        show_next = True

    # Формирование клавиатуры
    keyboard: InlineKeyboardMarkup = kb_input(
        state=loc_state.next,
        backstate=loc_state.id,
        show_next=show_next,
        buttons=loc.buttons
    )

    opts = LinkPreviewOptions(is_disabled=True)
    return text_message, keyboard, opts
