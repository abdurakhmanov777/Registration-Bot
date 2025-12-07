"""
Модуль обработки стартового состояния пользователя и формирования
клавиатуры на основе локализации.

Готовит текст приветственного сообщения, используя шаблон локализации,
и формирует инлайн-клавиатуру для дальнейшего взаимодействия
с пользователем.
"""

from typing import Any, Tuple

from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions

from app.core.bot.services.keyboards.user import kb_start

from ..context import MultiContext


async def handler_start(
    ctx: MultiContext,
) -> Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]:
    """
    Обрабатывает стартовое состояние пользователя.

    Формирует текст приветственного сообщения на основе данных локализации
    и создает инлайн-клавиатуру для дальнейшего взаимодействия.

    Parameters
    ----------
    ctx : MultiContext
        Контекст, содержащий данные пользователя, локализацию
        и параметры выполнения.

    Returns
    -------
    Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]
        Кортеж, содержащий текст сообщения, клавиатуру и параметры
        предпросмотра ссылок.
    """
    loc: Any = ctx.loc
    part1: str
    part2: str

    # Формируем текст сообщения на основе шаблона локализации
    part1, part2 = loc.messages.template.start
    text_message: str = f"{part1}{loc.event.name}{part2}"

    # Создаем клавиатуру на основе локализованных кнопок
    keyboard: InlineKeyboardMarkup = kb_start(buttons=loc.buttons)

    # Отключение предпросмотра ссылок для чистоты интерфейса
    preview_options = LinkPreviewOptions(is_disabled=True)

    return text_message, keyboard, preview_options
