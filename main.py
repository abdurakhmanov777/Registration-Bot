import asyncio

from loguru import logger

from app.bot_init import run_bot
from app.database.init_db import async_main


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
