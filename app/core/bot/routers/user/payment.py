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
from app.core.bot.services.keyboards.user import kb_payment_1
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

    user_state: bool | str | list[str] | None = await manage_user_state(
        message.from_user.id,
        "peek"
    )

    db_user: User | bool | None | int = await manage_user(
        tg_id=message.from_user.id,
        action="get"
    )

    if not isinstance(db_user, User) or not isinstance(user_state, str):
        return

    msg_id: User | bool | None | int = await manage_user(
        tg_id=message.from_user.id,
        action="msg_update",
        msg_id=message.message_id + 1
    )

    await handler_success(
        loc=loc,
        tg_id=message.from_user.id,
        event=message
    )
    if isinstance(msg_id, int) and msg_id != 0 and message.bot:
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except:
            pass

    await manage_user_state(
        message.from_user.id,
        "push",
        "100"
    )

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


    await callback.message.edit_text(
        text=loc.messages.payment,
        reply_markup=kb_payment_1(loc.buttons)
    )
    # prices: list[types.LabeledPrice] = [
    #     types.LabeledPrice(
    #         label="Оплата",
    #         amount=loc.event.payment.price * 100
    #     )
    # ]
    # await callback.message.bot.send_invoice(
    #     chat_id=callback.from_user.id,
    #     title=loc.event.name,
    #     description="Оплата участия",
    #     payload="order",
    #     provider_token=PROVIDER_TOKEN,
    #     currency=CURRENCY,
    #     prices=prices,
    # )

    await log(callback)
