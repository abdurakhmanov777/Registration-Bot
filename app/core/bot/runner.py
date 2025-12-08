"""
Модуль для запуска, остановки и проверки состояния Telegram-ботов.

Содержит функции для управления ботами через PollingManager, а также
регистрацию команд и настройку диспетчера.
"""

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types.user import User
from loguru import logger

from app.core.bot.services.polling.manager import PollingManager

from .commands import register_bot_commands
from .dispatcher import setup_dispatcher
from .services.polling import get_polling_manager


async def run_bot(
    api_token: str
) -> None:
    """Запускает Telegram-бота и его polling.

    Args:
        api_token (str): Токен API бота.
    """
    dp: Dispatcher = await setup_dispatcher()
    polling_manager: PollingManager = get_polling_manager()

    async with Bot(api_token) as bot:
        # Регистрируем команды бота
        await register_bot_commands(bot)

        async def on_startup() -> None:
            """Функция вызывается при запуске бота."""
            bot_info: User = await bot.get_me()
            logger.debug(f"Бот @{bot_info.username} запущен")

        async def on_shutdown() -> None:
            """Функция вызывается при остановке бота."""
            logger.debug("Бот остановлен")

        # Запуск polling через менеджер
        polling_manager.start_bot_polling(
            dp=dp,
            api_token=api_token,
            on_bot_startup=on_startup,
            on_bot_shutdown=on_shutdown,
        )

        # Ждем завершения polling
        while polling_manager.is_bot_running(api_token):
            await asyncio.sleep(1)


def stop_bot(
    api_token: str
) -> None:
    """Останавливает бота по API токену.

    Args:
        api_token (str): Токен API бота.
    """
    polling_manager: PollingManager = get_polling_manager()
    polling_manager.stop_bot_polling(api_token)


def is_bot_running(
    api_token: str
) -> bool:
    """Проверяет, запущен ли бот по API токену.

    Args:
        api_token (str): Токен API бота.

    Returns:
        bool: True, если бот запущен, иначе False.
    """
    polling_manager: PollingManager = get_polling_manager()
    return polling_manager.is_bot_running(api_token)
