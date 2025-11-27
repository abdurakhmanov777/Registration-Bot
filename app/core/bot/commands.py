"""
Модуль для регистрации команд Telegram-бота в приватных чатах.

Создаёт две отдельные клавиатуры команд:
- для обычных пользователей;
- для администраторов (с дополнительной командой /admin).
"""

from typing import Sequence

from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand
from loguru import logger

from app.config.settings import MAIN_ADMINS


async def register_bot_commands(
    bot: Bot,
) -> None:
    """Регистрирует отдельные клавиатуры команд для пользователей и админов.

    Обычные пользователи получают базовый набор команд. Администраторы
    получают отдельную клавиатуру с командой /admin.

    Args:
        bot (Bot): Экземпляр Telegram-бота.

    Returns:
        None: Функция не возвращает значения.
    """
    # Клавиатура для обычных пользователей
    user_keyboard: Sequence[BotCommand] = [
        BotCommand(
            command="start",
            description="Запуск или перезапуск бота",
        ),
        BotCommand(
            command="help",
            description="Техническая поддержка",
        ),
        BotCommand(
            command="id",
            description="Узнать ID чата",
        ),
    ]

    # Клавиатура для администраторов (включает /admin)
    admin_keyboard: Sequence[BotCommand] = [
        BotCommand(
            command="start",
            description="Запуск или перезапуск бота",
        ),
        BotCommand(
            command="help",
            description="Техническая поддержка",
        ),
        BotCommand(
            command="id",
            description="Узнать ID чата",
        ),
        BotCommand(
            command="admin",
            description="Админ-панель",
        ),
    ]

    # Установка клавиатуры для всех пользователей
    try:
        await bot.set_my_commands(
            commands=user_keyboard,
            scope=types.BotCommandScopeAllPrivateChats(),
        )
    except TelegramBadRequest:
        logger.warning(
            "Не удалось установить команды для обычных пользователей"
        )

    # Установка отдельной клавиатуры для каждого администратора
    for admin_id in MAIN_ADMINS:
        try:
            await bot.set_my_commands(
                commands=admin_keyboard,
                scope=types.BotCommandScopeChat(chat_id=admin_id),
            )
        except TelegramBadRequest:
            # Логируем, если чат администратора ещё не существует
            logger.warning(
                f"Невозможно установить команды админа ({admin_id})"
            )
