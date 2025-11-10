"""
Создание экземпляра Telegram-бота и очистка вебхуков.
"""

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import BOT_TOKEN


async def create_bot() -> Bot:
    """
    Создает экземпляр Bot и очищает старые вебхуки.

    Returns:
        Bot: Экземпляр бота с очищенной очередью обновлений.
    """
    bot = Bot(
        token=str(BOT_TOKEN),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await bot.delete_webhook()
    await bot.get_updates(offset=-1)
    return bot
