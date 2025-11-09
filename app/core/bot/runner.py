"""
Модуль запуска Telegram-бота.
"""

from aiogram import Bot, Dispatcher
from loguru import logger

from .commands import register_bot_commands
from .dispatcher import setup_dispatcher
from .factory import create_bot
from .logging_config import configure_logging


async def run_bot() -> None:
    """
    Инициализация и запуск Telegram-бота.

    Последовательность действий:
        1. Создание экземпляра бота.
        2. Регистрация команд бота.
        3. Настройка диспетчера.
        4. Запуск polling с колбэком on_startup.
        5. Корректное завершение сессии бота.
    """
    # Настройка логирования
    configure_logging()

    # Создание экземпляра бота
    bot: Bot = await create_bot()

    # Регистрация команд бота
    await register_bot_commands(bot)

    # Настройка диспетчера
    dp: Dispatcher = await setup_dispatcher()

    # Колбэк, который срабатывает после подключения бота
    async def on_startup(bot: Bot) -> None:
        logger.debug("Бот подключён и polling стартовал")

    # Регистрация колбэка
    dp.startup.register(on_startup)

    # Запуск polling
    await dp.start_polling(bot)

    # Корректное завершение сессии бота
    await bot.session.close()
