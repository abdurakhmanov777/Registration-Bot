"""
Регистрация команд Telegram-бота.
"""

from typing import Sequence

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def register_bot_commands(
    bot: Bot
) -> None:
    """
    Регистрирует команды Telegram-бота только для приватных чатов.

    Args:
        bot (Bot): Экземпляр Telegram-бота.
    """
    commands: Sequence[BotCommand] = [
        BotCommand(command="start", description="Запуск/перезапуск бота"),
        BotCommand(command="help", description="Техническая поддержка"),
        BotCommand(command="id", description="Узнать ID чата"),
    ]

    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeAllPrivateChats(),
    )
