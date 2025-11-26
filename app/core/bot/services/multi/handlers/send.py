"""
Модуль обработки состояния отправки финального сообщения с изображением.
"""

from io import BytesIO
from typing import Any, Optional

from aiogram import types
from aiogram.enums import ChatAction

from app.core.bot.services.generator import generate_image
from app.core.bot.services.generator.generator_code import generate_code
from app.core.bot.services.keyboards.user import kb_send
from app.core.bot.services.requests.user import manage_user
from app.core.database.models.user import User


async def handle_send(
    loc: Any,
    tg_id: int,
    event: Optional[types.CallbackQuery | types.Message]
) -> Optional[int]:
    """
    Обрабатывает состояние отправки финального сообщения с изображением.

    Args:
        ctx (MultiContext): Контекст с параметрами обработки.

    Returns:
        Optional[int]: ID отправленного сообщения (для закрепления),
            либо None, если отправка невозможна.
    """

    # Универсальный способ получить message
    message: Optional[types.MaybeInaccessibleMessageUnion]
    if isinstance(event, types.CallbackQuery):
        message = event.message
    else:
        message = event

    if not message or not message.bot:
        return None

    # Генерация кода (временно)
    user: User | bool | None | int = await manage_user(
        tg_id=tg_id,
        action="get"
    )
    if not isinstance(user, User):
        return
    code: int | None = generate_code(
        user_id=user.id,
        num_digits=3
    )

    # Анимация загрузки
    await message.bot.send_chat_action(
        chat_id=tg_id,
        action=ChatAction.UPLOAD_PHOTO
    )

    try:
        # Генерация изображения
        buffer: BytesIO = await generate_image(str(code))

        p1: str
        p2: str
        p1, p2 = loc.template.send
        caption: str = f"{p1}{code}{p2}"

        # Отправка фото
        msg: types.Message = await message.answer_photo(
            photo=types.BufferedInputFile(buffer.read(), filename="code.png"),
            caption=caption,
            parse_mode="HTML",
            # reply_markup=kb_send(buttons=loc.button)
        )

        # Закрепление сообщения
        await message.bot.pin_chat_message(
            chat_id=message.chat.id,
            message_id=msg.message_id
        )

        return msg.message_id

    except BaseException:
        return None
