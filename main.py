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
      3. Логирование ошибок и корректное завершение.
    """
    try:
        await init_db()
    except Exception as db_error:
        logger.exception(
            f"Ошибка при инициализации базы данных: {db_error}"
        )
        # Прерываем запуск, если база данных не готова
        return

    try:
        await run_bot()
    except asyncio.CancelledError:
        logger.info("Главный цикл отменен (asyncio.CancelledError)")
    except KeyboardInterrupt:
        logger.info("Главный цикл прерван пользователем (Ctrl+C)")
    except Exception as bot_error:
        logger.exception(f"Ошибка во время работы бота: {bot_error}")
    finally:
        logger.info("Приложение корректно завершило работу")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Главный цикл прерван пользователем (Ctrl+C)")
    except Exception as error:
        logger.exception(f"Аварийное завершение главного цикла: {error}")
