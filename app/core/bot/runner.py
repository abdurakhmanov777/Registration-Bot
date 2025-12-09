"""
Модуль для запуска и остановки Telegram-ботов, а также проверки их
состояния.

Предоставляет функции для управления жизненным циклом ботов через
PollingManager, включая регистрацию команд и настройку диспетчера.
"""

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types.user import User
from loguru import logger

from .commands import register_bot_commands
from .dispatcher import setup_dispatcher
from .services.polling import PollingManager, get_polling_manager


async def run_bot(
    api_token: str,
) -> bool:
    """Запускает Telegram-бота и его механизм polling.

    Parameters
    ----------
    api_token : str
        API-токен Telegram-бота.

    Returns
    -------
    bool
        `True`, если бот успешно запущен, иначе `False`.
    """
    try:
        dispatcher: Dispatcher = await setup_dispatcher()
        polling_manager: PollingManager = get_polling_manager()

        if polling_manager.is_bot_running(api_token):
            logger.warning("Бот запущен, повторный запуск отклонен")
            return False

        async with Bot(api_token) as bot:
            await register_bot_commands(bot)

            async def on_startup() -> None:
                """Обрабатывает запуск бота.

                Выполняется сразу после успешного старта polling.
                """
                bot_info: User = await bot.get_me()
                logger.debug(f"Бот @{bot_info.username} запущен")

            async def on_shutdown() -> None:
                """Обрабатывает остановку бота.

                Вызывается после завершения polling.
                """
                logger.debug("Бот остановлен")

            polling_manager.start_bot_polling(
                dp=dispatcher,
                api_token=api_token,
                on_bot_startup=on_startup,
                on_bot_shutdown=on_shutdown,
            )

            # Цикл ожидания, чтобы не завершать контекст до остановки бота.
            while polling_manager.is_bot_running(api_token):
                await asyncio.sleep(1)

        return True

    except Exception as error:
        logger.exception(f"Ошибка при запуске бота: {error}")
        return False


def stop_bot(
    api_token: str,
) -> bool:
    """Останавливает Telegram-бота по API-токену.

    Parameters
    ----------
    api_token : str
        API-токен бота, который требуется остановить.

    Returns
    -------
    bool
        `True`, если бот был остановлен, иначе `False`.
    """
    try:
        polling_manager: PollingManager = get_polling_manager()

        if not polling_manager.is_bot_running(api_token):
            logger.warning("Бот не запущен, оставнока отклонена")
            return False

        polling_manager.stop_bot_polling(api_token)
        return True

    except Exception as error:
        logger.exception(f"Ошибка при остановке бота: {error}")
        return False
