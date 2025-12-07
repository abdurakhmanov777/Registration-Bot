"""
Модуль обработки пользовательских сообщений Telegram-бота для приватных чатов.

Содержит обработчик входящих текстовых сообщений от пользователя.
Обеспечивает:
    - обработку шагов с типом "input";
    - интеграцию с динамической локализацией;
    - рендеринг текстов и клавиатур через функцию `multi`;
    - обновление предыдущего сообщения бота, чтобы сохранять единый UI-поток.
"""

from typing import Any

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from app.core.bot.routers.filters import ChatTypeFilter
from app.core.bot.services.logger import log
from app.core.bot.services.multi import multi

user_message: Router = Router()


@user_message.message(
    ChatTypeFilter(chat_type=["private"])
)
async def msg_user(
    message: types.Message,
    state: FSMContext
) -> None:
    """Обрабатывает входящее текстовое сообщение пользователя.

    Обработчик активируется только в приватных чатах.
    Если текущий шаг пользователя имеет тип ``input``, сообщение
    передаётся в функцию `multi` для формирования обновлённого текста,
    клавиатуры и настроек предпросмотра. Затем предыдущее сообщение
    бота (сохранённое по ``user_db.msg_id``) обновляется полученными данными.

    UI остаётся в одном сообщении, что делает интерфейс компактным
    и понятным для пользователя.

    Args:
        message (types.Message): Полученное текстовое сообщение от пользователя.
        state (FSMContext): Контекст FSM для доступа к локализации и данным пользователя.

    Returns:
        None
    """
    if not message.from_user or not message.bot:
        return

    # Получаем локализацию пользователя
    user_data: dict[str, Any] = await state.get_data()
    loc: Any | None = user_data.get("loc_user")
    user_db: Any = user_data.get("user_db")

    if not loc or not message.from_user:
        return

    tg_id: int = message.from_user.id

    user_state: list = user_db.state[-1]

    if not isinstance(user_state, str):
        return

    # Проверяем, что шаг пользователя ожидает ввод текста
    state_obj: Any | None = getattr(loc.steps, user_state, None)
    if not state_obj or state_obj.type != "input":
        return

    # Генерация текста сообщения, клавиатуры и параметров предпросмотра
    text_message: str
    keyboard_message: types.InlineKeyboardMarkup
    link_opts: types.LinkPreviewOptions

    text_message, keyboard_message, link_opts = await multi(
        state=state,
        value=user_state,
        tg_id=tg_id,
        data=message.text,
    )

    # Обновляем предыдущее сообщение с новым текстом и клавиатурой
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user_db.msg_id,
            text=text_message,
            reply_markup=keyboard_message,
            link_preview_options=link_opts
        )
    except Exception:
        pass

    await log(message)
