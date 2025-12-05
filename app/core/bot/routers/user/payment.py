"""
Модуль для обработки callback-запросов Telegram-бота.

Содержит обработчики для навигации по состояниям пользователя,
удаления сообщений, отправки данных, возврата к предыдущему состоянию
и отмены регистрации.
"""

from typing import Any, Dict

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext

from app.config.settings import CURRENCY, PROVIDER_TOKEN
from app.core.bot.routers.filters import ChatTypeFilter
from app.core.bot.services.keyboards.user import kb_payment
from app.core.bot.services.logger import log

user_payment: Router = Router()


@user_payment.pre_checkout_query()
async def process_pre_checkout_query(
    pre_checkout_query: types.PreCheckoutQuery,
    bot: Bot
) -> None:
    print(1111)
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True
    )


@user_payment.message()
async def aaa(
    message: types.Message
) -> None:

    await message.answer("Платёж успешно выполнен!")


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
            amount=100 * 100
        )
    ]
    await callback.message.bot.send_invoice(
        chat_id=callback.from_user.id,
        title=loc.event.name,
        description="Оплати участие",
        payload="order",
        provider_token=PROVIDER_TOKEN,
        currency=CURRENCY,
        prices=prices,
    )

    await log(callback)
