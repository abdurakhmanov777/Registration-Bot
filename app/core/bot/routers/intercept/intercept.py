from aiogram import Router
from aiogram.types import CallbackQuery, Message

from app.core.bot.routers.filters import InterceptFilter
from app.core.bot.routers.filters.chat_type import ChatTypeFilter
from app.core.bot.services.logger import log


def get_router_intercept() -> Router:

    intercept_handler: Router = Router()

    @intercept_handler.callback_query(
        ChatTypeFilter(chat_type=["private"]),
        InterceptFilter()
    )
    async def check_flag(
        callback: CallbackQuery,
        flag_bot: bool,
        flag_reg: bool,
    ) -> None:
        """
        Обработчик открытия настроек администратора.

        Args:
            event: Событие от пользователя (CallbackQuery или Message).
            block_info: Словарь активных флагов системного блока.
        """

        # Получаем первое сообщение для активного флага
        if flag_bot:
            text = "Технические шоколадки\n\nПопробуйте зайти через 10 минут"
        elif flag_reg:
            text = "К сожалению, регистрация закрыта"
        else:
            text = None

        # Если есть сообщение, показываем его пользователю
        if text is not None:
            await callback.answer(
                text=text,
                show_alert=True,
            )
        await log(callback)

    return intercept_handler
