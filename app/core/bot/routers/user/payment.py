"""
Модуль для обработки callback-запросов Telegram-бота.

Содержит обработчики для навигации по состояниям пользователя,
удаления сообщений, отправки данных, возврата к предыдущему состоянию
и отмены регистрации.
"""

from typing import Any, Dict

from aiogram import Bot, F, Router, types
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext

from app.config.settings import CURRENCY, PROVIDER_TOKEN
from app.core.bot.routers.filters import ChatTypeFilter
from app.core.bot.services.logger import log
from app.core.bot.services.multi import multi
from app.core.bot.services.multi.handlers.success import handler_success
from app.core.bot.services.requests.user.crud import manage_user
from app.core.bot.services.requests.user.state import manage_user_state
from app.core.database.models.user import User

user_payment: Router = Router()


@user_payment.pre_checkout_query()
async def process_pre_checkout_query(
    pre_checkout_query: types.PreCheckoutQuery,
    bot: Bot
) -> None:
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True
    )


@user_payment.message(F.successful_payment)
async def aaa(
    message: types.Message,
    state: FSMContext,
) -> None:
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")
    if not loc or not message.from_user:
        return
    # await message.edit_text()
    
@user_payment.callback_query(
    ChatTypeFilter(chat_type=["private"]),
    F.data == "payment"
)
async def clbk_payment(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    user_data: Dict[str, Any] = await state.get_data()
    loc: Any = user_data.get("loc_user")

    if not isinstance(
        callback.message, types.Message
    ) or not callback.message.bot:
        return
    await callback.answer()
    prices: list[types.LabeledPrice] = [
        types.LabeledPrice(
            label="Оплата",
            amount=loc.event.payment.price * 100
        )
    ]
    msg: types.Message = await callback.message.bot.send_invoice(
        chat_id=callback.from_user.id,
        title=loc.event.name,
        description="Оплата участия",
        payload="order",
        provider_token=PROVIDER_TOKEN,
        currency=CURRENCY,
        prices=prices,
    )

    if msg:
        await manage_user(
            tg_id=callback.from_user.id,
            action="update",
            msg_payment_id=msg.message_id
        )

    await log(callback)
