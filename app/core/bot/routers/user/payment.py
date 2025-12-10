"""
Модуль обработки callback-запросов Telegram-бота.

Содержит обработчики событий, связанных с оплатой, включая:
    - подтверждение pre-checkout запроса (этап перед оплатой);
    - обработку успешного платежа;
    - формирование и отправку invoice пользователю;
    - обновление состояния пользователя после оплаты.

Модуль используется в приватных чатах и интегрирован с системой
динамических состояний и локализацией.
"""

from typing import Any, Dict

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext

from app.config.settings import PROVIDER_TOKEN
from app.core.bot.routers.filters import ChatTypeFilter
from app.core.bot.services.logger import log
from app.core.bot.services.multi import multi


def get_router_user_payment() -> Router:

    router: Router = Router()

    @router.pre_checkout_query()
    async def process_pre_checkout_query(
        pre_checkout_query: types.PreCheckoutQuery,
        bot: Bot
    ) -> None:
        """Подтверждает pre-checkout запрос перед оплатой.

        Telegram требует подтверждения pre-checkout события, иначе
        пользователь не сможет завершить оплату.

        Args:
            pre_checkout_query (types.PreCheckoutQuery): Объект Telegram с данными о платеже.
            bot (Bot): Экземпляр бота для отправки ответа.

        Returns:
            None
        """
        await bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=True
        )

    @router.message(F.successful_payment)
    async def final(
        message: types.Message,
        state: FSMContext,
    ) -> None:
        """Обрабатывает успешный платеж.

        После подтвержденной Telegram оплаты обновляет состояние
        пользователя и вызывает функцию `multi` для выполнения шагов,
        связанных с завершением процесса регистрации.

        Args:
            message (types.Message): Сообщение с объектом `successful_payment`.
            state (FSMContext): Контекст FSM пользователя.

        Returns:
            None
        """
        user_data: Dict[str, Any] = await state.get_data()
        if not message.from_user:
            return
        await multi(
            state=state,
            value="100",
            tg_id=message.from_user.id,
            event=message
        )
        user_db: Any = user_data.get("user_db")
        user_db.state = user_db.state + ["100"]

    @router.callback_query(
        ChatTypeFilter(chat_type=["private"]),
        F.data == "payment"
    )
    async def payment(
        callback: types.CallbackQuery,
        state: FSMContext
    ) -> None:
        """Обрабатывает нажатие кнопки оплаты и отправляет пользователю invoice.

        Формирует данные платежа, используя локализацию и параметры события,
        и отправляет пользователю счёт. Сохраняет ID сообщения invoice для
        дальнейших операций.

        Args:
            callback (types.CallbackQuery): Callback-запрос от пользователя.
            state (FSMContext): Контекст FSM для доступа к данным пользователя.

        Returns:
            None
        """
        await callback.answer()
        user_data: Dict[str, Any] = await state.get_data()
        loc: Any = user_data.get("loc_user")
        user_db: Any = user_data.get("user_db")

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
            currency=loc.event.payment.currency,
            prices=prices,
        )

        user_db.msg_id_other = msg.message_id
        await log(callback)

    return router
