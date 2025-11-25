"""
Модуль обработки состояния ввода пользователя и формирования
сообщения с клавиатурой на основе локализации.
"""

import re
from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup

from app.bot.services.keyboards.user import kb_input
from app.bot.services.requests.data.crud import manage_data
from app.bot.utils.morphology.casing import lower_words
from app.bot.utils.morphology.inflection import inflect_text


async def handle_input(
    loc: Any,
    loc_state: Any,
    value: str,
    tg_id: int,
    data: str | None
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Обрабатывает состояние ввода пользователя и формирует сообщение
    и клавиатуру на основе шаблона локализации.

    Args:
        loc (Any): Объект локализации с шаблонами сообщений.
        loc_state (Any): Состояние пользователя для обработки.
        value (str): Ключ текущего состояния пользователя.
        tg_id (int): Telegram ID пользователя.
        data (str | None): Данные, введённые пользователем.

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Текст сообщения и объект
        клавиатуры для ответа пользователю.
    """
    format_: str = loc_state.format
    pattern: Any = loc_state.pattern
    base_text: str = loc_state.text
    template: Any = loc.template.input
    p1: Any
    p2: Any
    p3: Any

    error: bool = False

    # Проверяем введённые пользователем данные на соответствие шаблону
    if data is not None:
        regex: re.Pattern[Any] = re.compile(pattern)
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
        # Получаем существующие данные для ключа, если данные не введены
        data = await manage_data(tg_id=tg_id, action="get", key=base_text)

    flag: bool = False

    # Формируем текст сообщения в зависимости от наличия ошибки и данных
    if error:
        p1, p2 = template.error
        text_message: str = f"{p1}{format_}{p2}"

    elif not data:
        p1, p2, p3 = template.empty
        processed_text: str = await inflect_text(
            text=await lower_words(base_text, capitalize_first=False),
            case="винительный"
        )
        text_message: str = f"{p1}{processed_text}{p2}{format_}{p3}"

    else:
        flag = True
        p1, p2, p3 = template.filled
        text_message: str = f"{p1}{base_text}{p2}{data}{p3}"

    keyboard_message: InlineKeyboardMarkup = kb_input(
        state=loc_state.keyboard,
        backstate=value,
        show_next=flag,
        buttons=loc.button
    )

    return text_message, keyboard_message
