"""
Модуль для инициализации и запуска Telegram-бота с polling.
"""

import asyncio
import sys
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.types.user import User
from loguru import logger

from .commands import register_bot_commands
from .dispatcher import setup_dispatcher
from .factory import create_bot


class FilterAiogramStderr:
    """
    Класс для подавления ненужных сообщений stderr от Aiogram.

    Игнорирует:
    - "Failed to fetch updates"
    - "Sleep for ..."
    """

    def write(
        self,
        message: str
    ) -> None:
        """
        Обрабатывает строку сообщения.

        Args:
            message (str): Сообщение для обработки.
        """
        msg: str = message.strip()
        if not msg or "Failed to fetch updates" in msg or "Sleep for" in msg:
            return

    def flush(
        self
    ) -> None:
        """Метод заглушка для интерфейса file-like объектов."""
        pass


# Перенаправляем stderr в фильтр
sys.stderr = FilterAiogramStderr()


async def run_bot() -> None:
    """
    Асинхронная инициализация и запуск Telegram-бота.

    Функция:
        - Создает экземпляр бота
        - Регистрирует команды
        - Настраивает диспетчер
        - Запускает polling
        - Обрабатывает ошибки и закрывает сессию
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

            Args:
                bot (Bot): Экземпляр Telegram-бота.
            """
            bot_info: User = await bot.get_me()
            logger.debug(f"Бот @{bot_info.username} запущен")

        dp.startup.register(on_startup)

        # Запуск polling
        await dp.start_polling(bot)

    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.debug("Бот остановлен")
    except Exception as error:
        logger.exception(f"Ошибка при запуске бота: {error}")
    finally:
        if bot:
            try:
                await bot.session.close()
            except Exception as close_error:
                logger.exception(
                    f"Ошибка при закрытии сессии бота: {close_error}"
                )
