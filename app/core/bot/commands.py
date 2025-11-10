"""
Модуль для регистрации команд Telegram-бота в приватных чатах.
"""

from typing import Sequence

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def register_bot_commands(
    bot: Bot
) -> None:
    """
    Регистрирует команды Telegram-бота только для приватных чатов.

    Функция добавляет набор команд:
        - /start — запуск или перезапуск бота
        - /help — техническая поддержка
        - /id — узнать ID чата

    Args:
        bot (Bot): Экземпляр Telegram-бота.
    """
    # Список команд для регистрации
    commands: Sequence[BotCommand] = [
        BotCommand(
            command="start",
            description="Запуск/перезапуск бота"
        ),
        BotCommand(
            command="help",
            description="Техническая поддержка"
        ),
        BotCommand(
            command="id",
            description="Узнать ID чата"
        ),
    ]

    # Регистрируем команды только для приватных чатов
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeAllPrivateChats(),
    )
