"""
Модуль для создания экземпляра Telegram-бота и очистки вебхуков.
"""

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import BOT_TOKEN


async def create_bot() -> Bot:
    """
    Создает экземпляр Telegram-бота и очищает старые вебхуки.

    Функция:
        - Создает объект Bot с HTML-парсингом по умолчанию.
        - Удаляет старые вебхуки.
        - Сбрасывает очередь обновлений до последнего.

    Returns:
        Bot: Экземпляр Telegram-бота с очищенными вебхуками.
    """
    # Создаем объект бота с HTML-разметкой по умолчанию
    bot: Bot = Bot(
        token=str(BOT_TOKEN),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    # Удаляем старые вебхуки
    await bot.delete_webhook()

    # Сбрасываем очередь обновлений, чтобы не получать старые апдейты
    await bot.get_updates(offset=-1)

    return bot
