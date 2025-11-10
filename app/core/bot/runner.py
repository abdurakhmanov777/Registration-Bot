"""
Модуль для инициализации и запуска Telegram-бота с polling.
"""

from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.types.user import User
from loguru import logger

from .commands import register_bot_commands
from .dispatcher import setup_dispatcher
from .factory import create_bot


async def run_bot() -> None:
    """
    Асинхронная инициализация и запуск Telegram-бота.

    Последовательность действий:
        1. Создание экземпляра бота.
        2. Регистрация команд бота.
        3. Настройка диспетчера.
        4. Запуск polling с колбэком on_startup.
        5. Корректное завершение сессии бота.
    """
    bot: Optional[Bot] = None

    try:
        # Создаем экземпляр бота
        bot = await create_bot()

        # Регистрируем команды бота
        await register_bot_commands(bot)

        # Настройка диспетчера
        dp: Dispatcher = await setup_dispatcher()

        async def on_startup(
            bot: Bot,
        ) -> None:
            """
            Callback при запуске polling.

            Логирует успешный старт бота.
            """
            bot_info: User = await bot.get_me()
            logger.debug(f"Бот @{bot_info.username} запущен")

        # Регистрируем колбэк запуска
        dp.startup.register(on_startup)

        # Запуск polling
        await dp.start_polling(bot)

    except Exception as error:
        logger.exception(f"Ошибка при запуске бота: {error}")

    finally:
        # Закрываем сессию бота после завершения
        if bot:
            try:
                await bot.session.close()
            except Exception as close_error:
                logger.exception(
                    f"Ошибка при закрытии сессии бота: {close_error}"
                )
