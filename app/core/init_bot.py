import asyncio
import logging

from aiogram import Bot, Dispatcher
from loguru import logger

from app.keyboards.commands import bot_commands
from app.routers import init_routers
from config import BOT_TOKEN

# Отключаем шумные внутренние логи aiogram и aiohttp
logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("aiohttp.client").setLevel(logging.WARNING)
logging.getLogger("aiogram.event").setLevel(logging.WARNING)


async def run_bot() -> None:
    """
    Запуск Telegram-бота.
    Включает:
      - Создание бота и диспетчера
      - Регистрацию команд и роутеров
      - Запуск polling
    """
    bot: Bot | None = None
    try:
        # Создание бота
        bot = Bot(token=str(BOT_TOKEN))

        # Очистка старых вебхуков и очереди обновлений
        await bot.delete_webhook()
        await bot.get_updates(offset=-1)

        # Регистрация команд
        await bot_commands(bot)
        logger.debug("Команды бота зарегистрированы")

        # Инициализация диспетчера и роутеров
        dp: Dispatcher = init_routers()
        logger.debug("Роутеры и диспетчер инициализированы")

        # Запуск polling
        logger.debug("Бот включен, запускаем polling")
        await dp.start_polling(bot, dp_for_new_bot=dp)

    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.debug("Завершение работы по сигналу отмены или Ctrl+C")

    except Exception as e:
        logger.exception(f"Необработанная ошибка: {e}")

    finally:
        if bot is not None:
            await bot.session.close()
        logger.debug("Бот отключен")
