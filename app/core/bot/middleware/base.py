"""
Базовый middleware для Aiogram.

Модуль предоставляет универсальный middleware для обработки событий
Telegram-бота. Поддерживает фильтрацию типов сообщений, обновление
локализации, передачу дополнительных параметров и безопасное удаление
сообщений после обработки.
"""

from typing import Any, Awaitable, Callable, Dict, Literal, Optional, Set

from aiogram import BaseMiddleware
from aiogram.types import ContentType, Message

from app.core.bot.services.logger import log_error

from .refresh import refresh_fsm_data


class MwBase(BaseMiddleware):
    """
    Базовый middleware для обработки входящих событий.

    Middleware выполняет несколько функций:
    - фильтрует события по допустимым типам контента;
    - загружает данные локализации в зависимости от роли пользователя;
    - при необходимости удаляет сообщение после обработки;
    - добавляет дополнительные данные в объект `data`.

    Attributes:
        delete_event (bool): Флаг удаления сообщения после обработки.
        role (Literal["user", "admin"]): Роль, определяющая набор
            локализационных данных.
        extra_data (Dict[str, Any]): Дополнительные параметры,
            передаваемые в `data`.
        allowed_types (Set[str]): Разрешённые типы сообщений.
    """

    def __init__(
        self,
        delete_event: bool = False,
        role: Literal["user", "admin"] = "user",
        allowed_types: Optional[Set[str]] = None,
        **extra_data: Any,
    ) -> None:
        """
        Инициализация middleware.

        Parameters:
            delete_event (bool): Удалять ли сообщение после обработки.
            role (Literal["user", "admin"]): Роль для локализации.
            allowed_types (Optional[Set[str]]): Разрешённые типы контента.
            **extra_data (Any): Дополнительные параметры.
        """
        self.delete_event: bool = delete_event
        self.role: Literal["user", "admin"] = role
        self.extra_data: Dict[str, Any] = extra_data
        self.allowed_types: Set[str] = (
            {ContentType.TEXT} | (allowed_types or set())
        )

    async def __call__(
        self,
        handler: Callable[
            [Any, Dict[str, Any]],
            Awaitable[Any]
        ],
        event: Optional[Any] = None,
        data: Dict[str, Any] = {},
    ) -> Any:
        """
        Выполнение middleware перед вызовом хэндлера.

        Обрабатывает событие: фильтрует сообщения по типу, обновляет
        локализацию и вызывает хэндлер. В случае ошибки логирует событие.

        Parameters:
            handler (Callable): Функция-хэндлер для обработки события.
            event (Optional[Any]): Входящее событие Aiogram.
            data (Dict[str, Any]): Общий словарь данных.

        Returns:
            Any: Результат работы хэндлера.
        """

        data.update(self.extra_data)

        if (
            isinstance(event, Message)
            and event.content_type not in self.allowed_types
        ):
            try:
                await event.delete()
            except Exception:
                pass
            return None

        await refresh_fsm_data(
            data=data,
            event=event,
            role=self.role,
        )

        try:
            result: Any = await handler(event, data)

            if self.delete_event and isinstance(event, Message):
                try:
                    await event.delete()
                except Exception:
                    pass

            return result

        except Exception as error:
            await log_error(event, error=error)
            return None
