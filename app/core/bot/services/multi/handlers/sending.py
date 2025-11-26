from io import BytesIO
from typing import Any

from aiogram import types
from aiogram.enums import ChatAction

from app.core.bot.services.generator import generate_text_image
from app.core.bot.services.multi.context import MultiContext


async def handle_send(
    ctx: MultiContext
) -> int | None:
    """
    Обрабатывает состояние отправки финального сообщения с изображением.

    Args:
        ctx (MultiContext): Контекст обработки шага.

    Returns:
        int | None: ID отправленного сообщения (для закрепления), либо None.
    """

    event = ctx.event
    loc = ctx.loc
    tg_id = ctx.tg_id

    # Универсальный способ получить message
    message: types.MaybeInaccessibleMessageUnion | None
    if isinstance(event, types.CallbackQuery):
        message = event.message
    else:
        message = event

    if not message or not message.bot:
        return None

    # Здесь генерируется код — логика временная, заменишь позже
    code = 1

    # Анимация загрузки
    await message.bot.send_chat_action(
        chat_id=tg_id,
        action=ChatAction.UPLOAD_PHOTO
    )

    try:
        # Генерация изображения
        buffer: BytesIO = await generate_text_image(str(code))

        p1, p2 = loc.template.send
        caption = f"{p1}{code}{p2}"

        # Отправка фото
        msg: types.Message = await message.answer_photo(
            photo=types.BufferedInputFile(buffer.read(), filename="code.png"),
            caption=caption,
            parse_mode="HTML"
        )

        # Закрепление
        await message.bot.pin_chat_message(
            chat_id=message.chat.id,
            message_id=msg.message_id
        )

        return msg.message_id

    except BaseException:
        return None
