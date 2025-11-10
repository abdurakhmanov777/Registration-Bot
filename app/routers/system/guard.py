"""
Роутер-перехватчик для системных состояний Telegram-бота.

Использует фильтр SystemBlockFilter, который перехватывает входящие
сообщения и нажатия на кнопки, если бот находится в режиме
обслуживания или регистрация временно закрыта.
"""

from aiogram import F, Router
from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message
from loguru import logger

from app.filters import SystemBlockFilter

# Глобальные флаги состояния бота
MAINTENANCE_MODE: bool = False
REGISTRATION_CLOSED: bool = True

# Создаём роутер с высоким приоритетом
guard_router: Router = Router(name="guard_router")

# def admin_callback(
#     *filters: Any
# ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
#     """
#     Декоратор для обработки коллбеков в приватных чатах.
#     Добавляет фильтр ChatTypeFilter(chat_type=["private"]) и
#     фильтр администратора.

#     Args:
#         *filters (Any): Дополнительные фильтры для callback_query.

#     Returns:
#         Callable[[Callable[..., Any]], Callable[..., Any]]:
#         Декоратор для обработчика коллбека.
#     """
#     def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
#         return router.callback_query(
#             SystemBlockFilter(),
#             AdminFilter(),
#             *filters
#         )(func)

#     return decorator


@guard_router.message(SystemBlockFilter(), F.text)
async def handle_blocked_message(
    message: Message,
) -> None:
    """
    Обрабатывает сообщения при активной блокировке.

    Args:
        message (Message): Объект входящего сообщения.
    """
    if MAINTENANCE_MODE:
        logger.debug("Перехват сообщения: бот на техобслуживании.")
        await message.answer(
            "⚙️ Бот временно недоступен. Техническое обслуживание."
        )
        return

    if REGISTRATION_CLOSED:
        logger.debug("Перехват сообщения: регистрация закрыта.")
        await message.answer("🚫 Регистрация временно закрыта.")
        return


@guard_router.callback_query(SystemBlockFilter())
async def handle_blocked_callback(
    callback: CallbackQuery,
) -> None:
    """
    Обрабатывает нажатия на кнопки при активной блокировке.

    Args:
        callback (CallbackQuery): Объект callback-запроса.
    """
    if MAINTENANCE_MODE:
        logger.debug("Перехват callback: бот на техобслуживании.")
        await callback.answer(
            "⚙️ Бот на техническом перерыве",
            show_alert=True,
        )
        return

    if REGISTRATION_CLOSED:
        logger.debug("Перехват callback: регистрация закрыта.")
        await callback.answer(
            "🚫 Регистрация временно закрыта",
            show_alert=True,
        )
        return
