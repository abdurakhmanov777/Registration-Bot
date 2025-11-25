from io import BytesIO
from typing import Any, LiteralString

from aiogram.enums import ChatAction
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.bot.services.generator import generate_text_image


async def handle_send(
    loc: Any,
    tg_id: int,
    event: CallbackQuery | Message,
) -> int | None:
    # Определим бота и объект message вне зависимости от типа события
    message: Any | Message = event.message if isinstance(
        event, CallbackQuery
    ) else event

    if not message or not message.bot:
        return

    code = 1

    await message.bot.send_chat_action(
        chat_id=tg_id,
        action=ChatAction.UPLOAD_PHOTO
    )

    try:
        buffer: BytesIO = await generate_text_image(str(code))

        p1: Any
        p2: Any
        p1, p2 = loc.template.send
        caption: str = f"{p1}{code}{p2}"

        msg: Message = await message.answer_photo(
            photo=BufferedInputFile(buffer.read(), filename="code.png"),
            caption=caption,
            parse_mode='HTML'
        )

        await message.bot.pin_chat_message(
            chat_id=message.chat.id,
            message_id=msg.message_id
        )

        # await user_bot(tg_id=tg_id, bot_id=bot_id, action='upsert',
        # msg_id=msg.message_id)
        return msg.message_id
    except BaseException:
        pass
