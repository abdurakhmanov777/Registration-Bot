"""
Главная точка входа приложения.
"""

import asyncio

from loguru import logger

from app.core import init_db, run_bot


async def main() -> None:
    """
    Основная функция приложения.

    Выполняет:
        - Инициализацию базы данных
        - Запуск Telegram-бота
        - Обработку исключений и корректное завершение
    """
    try:
        # Инициализация базы данных
        await init_db()

        # Запуск бота
        await run_bot()

    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.warning("Главный цикл остановлен")

    except Exception as error:
        # Логирование аварийного завершения приложения
        logger.exception(f"Аварийное завершение приложения: {error}")

    finally:
        # Сообщение о завершении работы приложения
        logger.debug("Приложение завершило работу корректно")


if __name__ == "__main__":
    asyncio.run(main())
