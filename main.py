import asyncio

from loguru import logger

from app.core.runner import run_bot
from app.database import async_main


async def main() -> None:
    # Инициализация базы данных
    await async_main()

    # Запуск бота
    await run_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.debug("Главный цикл прерван (KeyboardInterrupt)")
