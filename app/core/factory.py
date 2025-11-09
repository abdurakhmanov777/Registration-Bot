"""
Создание экземпляра Telegram-бота и очистка вебхуков.
"""

from aiogram import Bot

from app.config import BOT_TOKEN


async def create_bot() -> Bot:
    """
    Создает экземпляр Bot и очищает старые вебхуки.

    Returns:
        Bot: Экземпляр бота с очищенной очередью обновлений.
    """
    bot = Bot(token=str(BOT_TOKEN))
    await bot.delete_webhook()
    await bot.get_updates(offset=-1)
    return bot
