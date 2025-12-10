"""
Модуль обработки состояния отправки финального сообщения с изображением.

Выполняет загрузку данных пользователя, генерацию кода, создание
итогового изображения и отправку финального сообщения с закреплением.
"""

from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Any, Dict, Optional, Tuple

from aiogram import types
from aiogram.enums import ChatAction
from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions

from app.core.bot.services.generator import generate_image
from app.core.bot.services.generator.generator_code import generate_code
from app.core.bot.services.keyboards import kb_success
from app.core.database.models import User

from ..context import MultiContext


async def handler_final(
    ctx: MultiContext,
) -> Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]:
    """
    Обрабатывает состояние отправки финального сообщения с изображением.

    Загружает данные пользователя, генерирует код, создает изображение
    и отправляет финальное сообщение с закреплением в чате.

    Parameters
    ----------
    ctx : MultiContext
        Контекст текущего состояния, содержащий объект локализации,
        событие и Telegram ID пользователя.

    Returns
    -------
    Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]
        Кортеж с идентификатором сообщения (пустая строка),
        разметкой клавиатуры и опциями предпросмотра ссылок.
    """

    # Универсальное извлечение сообщения
    message: Optional[types.MaybeInaccessibleMessageUnion]
    event: types.CallbackQuery | types.Message | None = ctx.event
    loc: Any = ctx.loc

    user_data: Dict[str, Any] = await ctx.state.get_data()
    user: list[str] = user_data["user_db"]
    if isinstance(event, types.CallbackQuery):
        message = event.message
    else:
        message = event

    if not message or not message.bot or not isinstance(user, User):
        return "", InlineKeyboardMarkup(
            inline_keyboard=[[]]
        ), LinkPreviewOptions()

    # Генерация кода
    code: Optional[int] = generate_code(
        user_id=user.id,
        num_digits=3,
    )

    # Отображение действия загрузки
    await message.bot.send_chat_action(
        chat_id=ctx.tg_id,
        action=ChatAction.UPLOAD_PHOTO,
    )

    # Генерация изображения
    image_buffer: BytesIO = await generate_image(str(code))

    # Формирование подписи
    template: Any = loc.messages.template.final
    info: Any = loc.event

    part1: str
    part2: str
    part3: str
    part1, part2, part3 = template.parts

    dt: datetime = datetime.strptime(
        f"{info.date} {info.time}",
        "%Y-%m-%d %H:%M:%S",
    )

    month_name: str = getattr(
        loc.months,
        str(dt.month - 1),
    )

    date_str: str = (
        f"{dt.day} {month_name} {dt.year}, "
        f"{dt.hour:02d}:{dt.minute:02d}"
    )

    info_text: str = (
        f"{template.names.address}{info.address}\n"
        f"{template.names.date}{date_str}"
    )

    flag: bool = not info.payment.status and info.confirm

    caption: str = (
        f"{part1}{code}"
        f"{part2}{info_text}"
        f"{part3}"
        f"{template.confirm if flag else ""}"
    )

    # Отправка изображения
    sent_message: types.Message = await message.answer_photo(
        photo=types.BufferedInputFile(
            image_buffer.read(),
            filename="code.png",
        ),
        caption=caption,
        parse_mode="HTML",
        reply_markup=kb_success(
            payment=loc.event.payment.status,
            buttons=loc.buttons
        ),
    )

    # Закрепление сообщения
    chat_id: int = message.chat.id
    try:
        await message.bot.pin_chat_message(
            chat_id=chat_id,
            message_id=sent_message.message_id,
        )
    except Exception:
        pass

    # return sent_message.message_id
    user_data: Dict[str, Any] = await ctx.state.get_data()
    user_db: Any = user_data.get("user_db")
    msg_id_old: int = user_db.msg_id
    user_db.msg_id = sent_message.message_id
    if isinstance(msg_id_old, int):
        try:
            await message.bot.delete_message(
                message.chat.id,
                msg_id_old
            )
        except Exception:
            pass

    tz = timezone(timedelta(hours=loc.event.timezone))
    user_db.date_registration = datetime.now(tz=tz)

    return "", InlineKeyboardMarkup(
        inline_keyboard=[[]]
    ), LinkPreviewOptions()
