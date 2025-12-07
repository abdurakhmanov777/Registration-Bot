"""
Модуль обработки состояния ввода пользователя.

Предоставляет функцию `handler_input`, которая валидирует введённые данные,
загружает или сохраняет их при необходимости и формирует итоговое сообщение
и клавиатуру для следующего шага.
"""

import re
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple, Union

from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions

from app.core.bot.services.keyboards.user import kb_dynamic
from app.core.bot.services.multi.context import MultiContext
from app.core.bot.utils.morphology.casing import lower_words
from app.core.bot.utils.morphology.inflection import inflect_text


async def handler_input(
    ctx: MultiContext,
) -> Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]:
    """
    Обрабатывает состояние ввода пользователя и формирует сообщение.

    Выполняет валидацию пользовательского ввода, сохраняет данные при
    успешной проверке, извлекает данные при их отсутствии и формирует
    корректное текстовое сообщение на основе шаблонов локализации.

    Args:
        ctx (MultiContext): Контекст шага сценария, содержащий
            локализацию, состояние шага, ID пользователя и данные.

    Returns:
        Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]:
            Сообщение, клавиатура и настройки предпросмотра ссылок.
    """
    loc: Any = ctx.loc
    loc_state: Any = ctx.loc_state
    tg_id: int = ctx.tg_id
    user_input: Optional[Union[str, datetime]] = ctx.data

    format_: str = loc_state.data.format
    pattern: str = loc_state.data.pattern
    base_text: str = loc_state.text
    value_type: str = loc_state.data.type
    template: Any = loc.messages.template.input

    error_occurred: bool = False
    show_next: bool = loc_state.data.required
    part1: str
    part2: str
    part3: str
    user_data: Dict[str, Any] = await ctx.state.get_data()
    data_db: Any = user_data.get("data_db")

    # Проверяем пользовательский ввод через регулярное выражение
    if user_input is not None:
        # if value_type.lower() == "datetime" and min_age is not None:
        #     birth_date: datetime = cast_value
        #     today: date = date.today()
        #     age: int = today.year - birth_date.year - (
        #         (today.month, today.day) < (birth_date.month,
        #                                     birth_date.day)
        #     )
        #     if age < min_age:
        #         # Возраст меньше минимально допустимого
        #         logger.error(
        #             f"Возраст {age} меньше минимально допустимого "
        #             f"{min_age}"
        #         )
        #         return None
        if re.fullmatch(pattern, user_input):
            if await type_check(
                value=user_input,
                value_type=value_type
            ):
                data_db[base_text] = user_input
            else:
                error_occurred = True
        else:
            error_occurred = True
    else:
        # Если пользователь ничего не ввёл, пробуем взять сохранённые данные
        user_input = data_db.get(base_text, None)

    # Формируем текст сообщения в зависимости от результата проверки
    if error_occurred:
        part1, part2 = template.error
        text_message: str = f"{part1}{format_}{part2}"
        show_next = False

    elif not user_input:
        part1, part2, part3 = template.empty

        processed_text: str = await inflect_text(
            text=await lower_words(
                base_text,
                capitalize_first=False,
            ),
            case="винительный",
        )

        text_message = (
            f"{part1}{processed_text}{part2}{format_}{part3}"
        )
        show_next = False

    else:
        # Поле заполнено корректно
        part1, part2, part3 = template.filled
        text_message = (
            f"{part1}{base_text}{part2}{user_input}{part3}"
        )
        show_next = True

    keyboard: InlineKeyboardMarkup = kb_dynamic(
        buttons=loc.buttons,
        state=loc_state.next,
        backstate=loc_state.id,
        show_next=show_next,
    )

    opts: LinkPreviewOptions = LinkPreviewOptions(is_disabled=True)

    return text_message, keyboard, opts


async def type_check(
    value: str,
    value_type: str
) -> bool:
    type_map: Dict[str, Callable[[str], Any]] = {
        "int": int,
        "bool": lambda v: v.lower() == "true",
        "date": lambda v: datetime.strptime(v, "%d.%m.%Y"),
        "time": lambda v: datetime.strptime(v, "%d.%m.%Y %H:%M:%S"),
        "str": str
    }
    caster: Optional[Callable[[str], Any]] = type_map.get(
        value_type.lower()
    )
    if not caster:
        return False

    try:
        caster(value)
        return True
    except BaseException:
        return False
