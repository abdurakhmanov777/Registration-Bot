"""
Главная точка входа приложения.

Модуль выполняет инициализацию базы данных и запуск Telegram-бота.
"""

import asyncio

from loguru import logger

from app.config.settings import BOT_TOKEN
from app.core import init_db, run_bot


async def main() -> None:
    """
    Основная асинхронная функция приложения.

    Выполняет последовательную инициализацию базы данных и запуск
    Telegram-бота. Обеспечивает корректную обработку исключений
    и завершение работы приложения.

    Returns:
        None: Функция не возвращает значения.
    """
    try:
        # Инициализация базы данных перед запуском бота.
        await init_db()

        # Запуск Telegram-бота.
        # await run_bot(api_tokens=BOT_TOKEN)
        await run_bot(api_tokens=[
            BOT_TOKEN,
            "7729098959:AAEnRW7i975wS-CubSS_SC_2xchQcJ_lnkI"
        ])

    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.warning("Главный цикл остановлен пользователем")

    except Exception as error:
        # Логирование аварийного завершения для диагностики причин сбоя.
        logger.exception(f"Аварийное завершение приложения: {error}")

    finally:
        # Гарантированное сообщение о завершении работы приложения.
        logger.debug("Приложение завершило работу корректно")


if __name__ == "__main__":
    asyncio.run(main())
