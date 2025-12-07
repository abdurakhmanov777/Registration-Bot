"""
Модуль обработки состояния выбора пользователя.

Предоставляет функцию `handler_select`, формирующую сообщение и клавиатуру
для выбора пользователя на основе текущей локализации.
"""

from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions

from app.core.bot.services.keyboards.user import kb_select

from ..context import MultiContext


async def handler_select(
    ctx: MultiContext,
) -> Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]:
    """
    Обрабатывает состояние выбора и формирует сообщение и клавиатуру.

    Создаёт текст сообщения на основе шаблона локализации и генерирует
    клавиатуру выбора для пользователя.

    Args:
        ctx (MultiContext): Контекст шага сценария, содержащий локализацию,
            состояние шага, идентификатор пользователя и другие параметры.

    Returns:
        Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]:
            Сформированное сообщение, клавиатура выбора и параметры
            предпросмотра ссылок.
    """
    loc: Any = ctx.loc
    loc_state: Any = ctx.loc_state
    part1: str
    part2: str

    base_text: str = loc_state.text
    part1, part2 = loc.messages.template.select

    # Формируем сообщение на основе шаблона
    text_message: str = f"{part1}{base_text}{part2}"

    # Генерируем клавиатуру выбора
    keyboard: InlineKeyboardMarkup = kb_select(
        name=base_text,
        options=loc_state.options,
        buttons=loc.buttons,
    )
    opts: LinkPreviewOptions = LinkPreviewOptions(is_disabled=True)

    return text_message, keyboard, opts
