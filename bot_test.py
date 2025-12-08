"""
Тест запуска и остановки Telegram-бота через терминал.

При запуске программы можно вводить:
    1 - запустить бота
    0 - остановить бота
    q - выйти из теста
"""

import asyncio
from typing import Optional

from loguru import logger

from app.config.settings import BOT_TOKEN
from app.core.bot.runner import is_bot_running, run_bot, stop_bot


async def terminal_test() -> None:
    """Интерактивный тест запуска и остановки бота через терминал."""

    while True:
        cmd: str = await asyncio.to_thread(input)

        if cmd == "1":
            if is_bot_running(BOT_TOKEN):
                logger.info("Бот уже запущен")
            else:
                logger.info("Запуск бота...")
                # Запуск бота в фоне
                asyncio.create_task(run_bot(BOT_TOKEN))

        elif cmd == "0":
            if is_bot_running(BOT_TOKEN):
                logger.info("Остановка бота...")
                stop_bot(BOT_TOKEN)
            else:
                logger.info("Бот не запущен")

        elif cmd.lower() == "q":
            logger.info("Выход из теста")
            if is_bot_running(BOT_TOKEN):
                stop_bot(BOT_TOKEN)
            break

        else:
            print("Неизвестная команда. Используйте 1, 0 или q.")


if __name__ == "__main__":
    try:
        asyncio.run(terminal_test())
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.warning("Тест прерван пользователем")
