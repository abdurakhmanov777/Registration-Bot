"""
Главная точка входа приложения.
"""

import asyncio

from loguru import logger

from app.core import init_db, run_bot


async def main() -> None:
    """
    Основная функция приложения.

    Последовательность действий:
        1. Инициализация базы данных.
        2. Запуск Telegram-бота.
    """
    try:
        # Инициализация базы данных
        await init_db()

        # Запуск бота
        await run_bot()

    except asyncio.CancelledError:
        logger.info("Главный цикл отменен (CancelledError)")
    except KeyboardInterrupt:
        logger.info("Главный цикл прерван пользователем (Ctrl+C)")
    except Exception as error:
        logger.exception(f"Аварийное завершение приложения: {error}")
    finally:
        logger.info("Приложение корректно завершило работу")


if __name__ == "__main__":
    asyncio.run(main())
