"""
Модуль для управления опросом Telegram-ботов через asyncio.

Содержит класс PollingManager для запуска, остановки и проверки
активных ботов
"""

import asyncio
from asyncio import Task
from typing import Any, Awaitable, Callable, Dict, List, Optional

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.dispatcher.dispatcher import DEFAULT_BACKOFF_CONFIG, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import User
from aiogram.utils.backoff import BackoffConfig
from loguru import logger


class PollingManager:
    """Менеджер для запуска и контроля опроса Telegram-ботов."""

    def __init__(self) -> None:
        """Инициализация менеджера с пустыми словарями задач и ботов."""
        self.tasks: Dict[str, Task] = {}
        self.api_to_bot_id: Dict[str, int] = {}

    def active_bots_count(self) -> int:
        """
        Возвращает количество активных ботов.

        Returns
        -------
        int
            Количество ботов, которые в данный момент запущены.
        """
        return len(self.tasks)

    def active_api_tokens(self) -> List[str]:
        """
        Возвращает список токенов API активных ботов.

        Returns
        -------
        List[str]
            Список токенов API.
        """
        return list(self.tasks.keys())

    def start_bot_polling(
        self,
        dp: Dispatcher,
        api_token: str,
        polling_timeout: int = 10,
        handle_as_tasks: bool = True,
        backoff_config: BackoffConfig = DEFAULT_BACKOFF_CONFIG,
        allowed_updates: Optional[List[str]] = None,
        on_bot_startup: Optional[Callable[[], Awaitable[Any]]] = None,
        on_bot_shutdown: Optional[Callable[[], Awaitable[Any]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Запускает опрос бота в отдельной асинхронной задаче.

        Parameters
        ----------
        dp : Dispatcher
            Диспетчер Aiogram для обработки апдейтов.
        api_token : str
            Токен API бота.
        polling_timeout : int, optional
            Таймаут опроса, по умолчанию 10.
        handle_as_tasks : bool, optional
            Обрабатывать апдейты как задачи.
        backoff_config : BackoffConfig, optional
            Конфигурация backoff.
        allowed_updates : list[str], optional
            Список разрешенных типов апдейтов.
        on_bot_startup : Callable[[], Awaitable[Any]], optional
            Функция запуска бота.
        on_bot_shutdown : Callable[[], Awaitable[Any]], optional
            Функция завершения работы бота.
        **kwargs : Any
            Дополнительные аргументы для dp._polling.
        """
        if self.is_bot_running(api_token):
            return

        task: Task[None] = asyncio.create_task(
            self._run_polling(
                dp=dp,
                api_token=api_token,
                polling_timeout=polling_timeout,
                handle_as_tasks=handle_as_tasks,
                backoff_config=backoff_config,
                allowed_updates=allowed_updates,
                on_bot_startup=on_bot_startup,
                on_bot_shutdown=on_bot_shutdown,
                **kwargs,
            )
        )
        self.tasks[api_token] = task

    async def _run_polling(
        self,
        dp: Dispatcher,
        api_token: str,
        polling_timeout: int,
        handle_as_tasks: bool,
        backoff_config: BackoffConfig,
        allowed_updates: Optional[List[str]],
        on_bot_startup: Optional[Callable[[], Awaitable[Any]]] = None,
        on_bot_shutdown: Optional[Callable[[], Awaitable[Any]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Выполняет опрос бота и обрабатывает апдейты.

        Parameters
        ----------
        dp : Dispatcher
            Диспетчер Aiogram для апдейтов.
        api_token : str
            Токен API бота.
        polling_timeout : int
            Таймаут опроса.
        handle_as_tasks : bool
            Обрабатывать апдейты как задачи.
        backoff_config : BackoffConfig
            Настройка backoff.
        allowed_updates : list[str] | None
            Разрешенные апдейты.
        on_bot_startup : Callable[[], Awaitable[Any]] | None
            Функция запуска.
        on_bot_shutdown : Callable[[], Awaitable[Any]] | None
            Функция остановки.
        **kwargs : Any
            Дополнительные аргументы для dp._polling.
        """
        async with Bot(
            token=api_token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML
            )
        ) as bot:
            try:
                # Удаляем старые вебхуки и сбрасываем очередь обновлений
                await bot.delete_webhook()
                await bot.get_updates(offset=-1)

                user: User = await bot.me()
                self.api_to_bot_id[api_token] = user.id

                if on_bot_startup:
                    await on_bot_startup()

                await dp._polling(
                    bot=bot,
                    handle_as_tasks=handle_as_tasks,
                    polling_timeout=polling_timeout,
                    backoff_config=backoff_config,
                    allowed_updates=allowed_updates,
                    **kwargs,
                )

            except Exception as error:
                logger.exception(
                    "Unexpected error in polling task for token "
                    f"{api_token}: {error}"
                )

            finally:
                if on_bot_shutdown:
                    await on_bot_shutdown()
                self.tasks.pop(api_token, None)
                self.api_to_bot_id.pop(api_token, None)

    def stop_bot_polling(self, api_token: str) -> None:
        """
        Останавливает опрос бота по токену API.

        Parameters
        ----------
        api_token : str
            Токен API бота.
        """
        task: Optional[Task[Any]] = self.tasks.get(api_token)
        if task and not task.done():
            task.cancel()

    def is_bot_running(self, api_token: str) -> bool:
        """
        Проверяет, запущен ли бот.

        Parameters
        ----------
        api_token : str
            Токен API бота.

        Returns
        -------
        bool
            True, если бот запущен, иначе False.
        """
        task: Optional[Task[Any]] = self.tasks.get(api_token)
        return task is not None and not task.done()
