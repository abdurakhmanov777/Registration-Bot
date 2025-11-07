from typing import Sequence, Tuple

from aiogram import Bot
from aiogram.types import (BotCommand, BotCommandScope,
                           BotCommandScopeAllGroupChats,
                           BotCommandScopeAllPrivateChats)


async def bot_commands(
    bot: Bot
) -> None:
    """
    Регистрирует команды бота для приватных чатов и групп.

    Args:
        bot (Bot): Экземпляр Telegram-бота.
    """
    command_sets: Sequence[Tuple[
        BotCommandScope, list[BotCommand]]
    ] = [
        (BotCommandScopeAllPrivateChats(), [
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
        ]),
        (BotCommandScopeAllGroupChats(), [
            BotCommand(
                command="id",
                description="Узнать ID чата"
            ),
        ]),
    ]

    for scope, commands in command_sets:
        await bot.set_my_commands(commands=commands, scope=scope)
