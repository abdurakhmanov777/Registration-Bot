"""
Модуль обработки финального состояния пользователя и формирования итогового
сообщения с клавиатурой.
"""

from typing import Any, Dict, List, Tuple

from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions

from app.core.bot.services.keyboards.user import kb_end
from app.core.bot.services.multi.context import MultiContext
from app.core.bot.services.requests.data import manage_data_list
from app.core.bot.services.requests.user import manage_user_state


async def handle_end(
    ctx: MultiContext,
) -> Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]:
    """
    Обрабатывает состояние пользователя и формирует итоговое сообщение.

    Получает список всех состояний пользователя, фильтрует их и формирует
    текст на основе шаблона локализации и данных пользователя. Формирует
    клавиатуру завершения.

    Args:
        ctx (MultiContext): Контекст с параметрами обработки.

    Returns:
        Tuple[str, InlineKeyboardMarkup]: Сообщение и клавиатура.
    """
    states: bool | str | List[str] | None = await manage_user_state(
        tg_id=ctx.tg_id,
        action="get_state",
    )

    if not isinstance(states, list):
        raise ValueError(
            f"Некорректный формат состояний пользователя: {states!r}"
        )
    loc: Any = ctx.loc
    # Формируем список ключей данных, которые нужно оставить
    keep_keys: List[str] = [
        data.text
        for state in states
        if (data := getattr(loc.steps, state, None)) is not None
        and getattr(data, "type", None) not in ("start", "end")
        and getattr(data, "text", None) is not None
    ]

    # Получаем словарь данных пользователя, оставляя только нужные ключи
    data_list: Dict[str, Any] = await manage_data_list(
        tg_id=ctx.tg_id,
        keep_keys=keep_keys,
    )

    # Формируем текст блоков данных
    items_text: str = "\n\n".join(
        f"🔹️ {key}: {value}" for key, value in data_list.items()
    )

    # Получаем шаблон локализации для начала и конца сообщения
    start_template: str
    end_template: str
    start_template, end_template = loc.messages.template.end

    text_message: str = f"{start_template}{items_text}{end_template}"

    # Формируем клавиатуру завершения
    keyboard: InlineKeyboardMarkup = kb_end(buttons=loc.buttons)

    opts = LinkPreviewOptions(is_disabled=True)
    return text_message, keyboard, opts
