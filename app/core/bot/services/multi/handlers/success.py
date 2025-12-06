"""
Модуль обработки состояния отправки финального сообщения с изображением.

Выполняет загрузку данных пользователя, генерацию кода, создание
итогового изображения и отправку финального сообщения с закреплением.
"""

from datetime import datetime
from io import BytesIO
from typing import Any, Optional, Union

from aiogram import Bot, types
from aiogram.enums import ChatAction

from app.config.settings import CURRENCY, PROVIDER_TOKEN
from app.core.bot.services.generator import generate_image
from app.core.bot.services.generator.generator_code import generate_code
from app.core.bot.services.keyboards.user import kb_success
from app.core.bot.services.requests.user import manage_user
from app.core.database.models.user import User


async def handler_success(
    loc: Any,
    tg_id: int,
    event: Optional[
        Union[
            types.CallbackQuery,
            types.Message,
        ]
    ],
) -> Optional[int]:
    """
    Обрабатывает состояние отправки финального сообщения с изображением.

    Загружает данные пользователя, генерирует код, создает изображение
    и отправляет финальное сообщение. Сообщение закрепляется в чате.

    Parameters
    ----------
    loc : Any
        Объект локализации, содержащий шаблоны и данные события.
    tg_id : int
        Telegram ID пользователя.
    event : CallbackQuery | Message | None
        Исходное событие, содержащее сообщение или callback.

    Returns
    -------
    Optional[int]
        Идентификатор отправленного сообщения или None при ошибке.
    """

    # Универсальное извлечение сообщения
    message: Optional[types.MaybeInaccessibleMessageUnion]
    if isinstance(event, types.CallbackQuery):
        message = event.message
    else:
        message = event

    # Проверка доступности message и его бота
    if message is None or message.bot is None:
        return None

    # Получение пользователя
    user_result: Union[User, bool, None, int] = await manage_user(
        tg_id=tg_id,
        action="get",
    )
    user: Optional[User] = user_result if isinstance(
        user_result, User) else None
    if user is None:
        return None

    # Генерация кода
    code: Optional[int] = generate_code(
        user_id=user.id,
        num_digits=3,
    )

    # Отображение действия загрузки
    await message.bot.send_chat_action(
        chat_id=tg_id,
        action=ChatAction.UPLOAD_PHOTO,
    )

    # Генерация изображения
    image_buffer: BytesIO = await generate_image(str(code))

    # Формирование подписи
    template: Any = loc.messages.template.success
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

    caption: str = (
        f"{part1}{code}"
        f"{part2}{info_text}"
        f"{part3}"
    )

    # Отправка изображения
    sent_message: types.Message = await message.answer_photo(
        photo=types.BufferedInputFile(
            image_buffer.read(),
            filename="code.png",
        ),
        caption=caption,
        parse_mode="HTML",
        reply_markup=kb_success(loc.buttons),
    )

    # Закрепление сообщения
    chat_id: int = message.chat.id
    try:
        await message.bot.pin_chat_message(
            chat_id=chat_id,
            message_id=sent_message.message_id,
        )
    except:
        pass

    # if loc.event.payment.status:
    #     prices: list[types.LabeledPrice] = [
    #         types.LabeledPrice(
    #             label="Оплата",
    #             amount=loc.event.payment.price * 100
    #         )
    #     ]

    #     bot: Bot | None = None
    #     if isinstance(event, types.Message):
    #         bot: Bot | None = event.bot
    #     elif isinstance(event, types.CallbackQuery) and event.message is not None:
    #         bot = event.message.bot
    #     if bot:
    #         msg: types.Message = await bot.send_invoice(
    #             chat_id=tg_id,
    #             title=loc.event.name,
    #             description="Оплата участия",
    #             payload="order",
    #             provider_token=PROVIDER_TOKEN,
    #             currency=CURRENCY,
    #             prices=prices,
    #         )
    #         await manage_user(
    #             tg_id=tg_id,
    #             action="update",
    #             msg_payment_id=msg.message_id
    #         )

    return sent_message.message_id
