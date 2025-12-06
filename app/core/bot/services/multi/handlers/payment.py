"""
Модуль обработки финального состояния пользователя.

Предоставляет функцию `handler_payment`, которая формирует итоговое сообщение
пользователю на основе сохранённых данных, шаблонов локализации и
клавиатуры завершения.
"""

from typing import Any, Tuple

from aiogram import Bot, types
from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions

from app.config.settings import CURRENCY, PROVIDER_TOKEN
from app.core.bot.services.keyboards.user import kb_payment_1
from app.core.bot.services.multi.context import MultiContext
from app.core.bot.services.requests.data import manage_data_list
from app.core.bot.services.requests.user import manage_user_state
from app.core.bot.services.requests.user.crud import manage_user


async def handler_payment(
    ctx: MultiContext,
) -> Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]:
    """
    Формирует итоговое сообщение пользователя по завершении сценария.

    Получает список состояний пользователя, отбирает те, которые содержат
    данные, загружает соответствующие значения и формирует финальный блок
    текста с учётом шаблонов локализации.

    Args:
        ctx (MultiContext): Контекст шага многошагового сценария, включающий
            локализацию, ID пользователя и связанные данные.

    Returns:
        Tuple[str, InlineKeyboardMarkup, LinkPreviewOptions]:
            Итоговое сообщение, финальная клавиатура и настройки предпросмотра.
    """

    loc: Any = ctx.loc
    tg_id: Any = ctx.tg_id
    event: types.CallbackQuery | types.Message | None = ctx.event
    text_message: str = loc.messages.payment

    # Создаём финальную клавиатуру
    keyboard: types.InlineKeyboardMarkup = kb_payment_1(
        buttons=loc.buttons
    )

    opts: types.LinkPreviewOptions = types.LinkPreviewOptions(is_disabled=True)

    prices: list[types.LabeledPrice] = [
        types.LabeledPrice(
            label="Оплата",
            amount=loc.event.payment.price * 100
        )
    ]

    bot: Bot | None = None
    if isinstance(event, types.Message):
        bot: Bot | None = event.bot
    elif isinstance(event, types.CallbackQuery) and event.message is not None:
        bot = event.message.bot
    if bot:
        msg: types.Message = await bot.send_invoice(
            chat_id=tg_id,
            title=loc.event.name,
            description="Оплата участия",
            payload="order",
            provider_token=PROVIDER_TOKEN,
            currency=CURRENCY,
            prices=prices,
        )
        await manage_user(
            tg_id=tg_id,
            action="update",
            msg_payment_id=msg.message_id
        )

    return text_message, keyboard, opts
