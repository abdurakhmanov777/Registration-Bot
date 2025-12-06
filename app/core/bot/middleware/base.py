"""
Базовый middleware для Aiogram.

Поддерживает:
    - подсчёт вызовов хэндлера,
    - удаление события после обработки,
    - передачу доп. параметров в data,
    - проверку роли администратора,
    - удаление сообщений с неподдерж. типами,
    - динамическое управление разрешёнными типами.
"""

from typing import Any, Awaitable, Callable, Literal, Optional, Set, Union

from aiogram import BaseMiddleware, Bot
from aiogram.types import CallbackQuery, ContentType, Message
from aiogram.types.user import User as TgUser

from app.core.bot.services.logger import log_error
from app.core.bot.services.requests.user.crud import manage_user
from app.core.database.models.user import User

from .refresh import refresh_fsm_data


class MwBase(BaseMiddleware):
    """
    Базовый middleware для обработки событий.

    Args:
        delete_event (bool): Удалять событие после обработки.
        role (Literal["user","admin"]): Роль для локализации.
        allowed_types (Optional[Set[str]]): Разрешённые типы сообщений.
        **extra_data: Доп. параметры для передачи в data.
    """

    def __init__(
        self,
        delete_event: bool = False,
        role: Literal["user", "admin"] = "user",
        allowed_types: Optional[Set[str]] = None,
        **extra_data: Any,
    ) -> None:
        self.counter: int = 0
        self.delete_event: bool = delete_event
        self.role: Literal["user", "admin"] = role
        self.extra_data: dict[str, Any] = extra_data
        # Разрешённые типы сообщений
        self.allowed_types: Set[str] = {ContentType.TEXT}
        if allowed_types:
            self.allowed_types.update(allowed_types)

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Optional[Any] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Основной метод middleware.

        Загружает локализацию, обновляет данные и проверяет роль.
        Удаляет сообщения с неподдерживаемыми типами.

        Args:
            handler (Callable[[Any, dict[str, Any]], Awaitable[Any]]):
                Хэндлер для обработки события.
            event (Optional[Any]): Событие Message или CallbackQuery.
            data (Optional[dict[str, Any]]): Данные между middleware
                и хэндлером.

        Returns:
            Any: Результат работы хэндлера.
        """
        if event is None:
            return await handler(event, data or {})

        # Фильтруем сообщения по разрешённым типам
        if isinstance(
            event,
            Message
        ) and event.content_type not in self.allowed_types:
            try:
                await event.delete()
            except Exception:
                pass
            return None

        # Инициализация data
        data = data or {}
        self.counter += 1

        # Обновляем счётчик и добавляем доп. данные
        data["counter"] = self.counter
        data.update(self.extra_data)

        # Загружаем локализацию в зависимости от роли
        await refresh_fsm_data(data, event, role=self.role)

        await delete_stored_message(event=event)
        try:
            # Вызываем хэндлер
            result: Any = await handler(event, data)
            # Удаляем событие после обработки, если включено
            if self.delete_event and hasattr(event, "delete"):
                try:
                    await event.delete()
                except Exception:
                    pass

            return result
        except Exception as e:
            # Логируем ошибки
            await log_error(event, error=e)


async def delete_stored_message(
    event: Union[Message, CallbackQuery]
) -> None:
    """
    Удаляет сообщение, id которого хранится в БД,
    основываясь на tg_id пользователя.
    """
    # from_user есть всегда
    user: TgUser | None = event.from_user
    if user is None:  # защита для статического анализатора
        return

    user_id: int = user.id

    bot: Bot | None = event.bot
    if bot is None:
        return

    # --- Получаем chat_id корректно ---
    if isinstance(event, CallbackQuery):
        if event.message is None:  # защита для Pylance
            return
        chat_id: int = event.message.chat.id
    else:
        chat_id: int = event.chat.id

    # --- Получаем id сообщения из БД ---
    msg_payment_id: User | bool | None | int = await manage_user(
        tg_id=user_id,
        action="msg_payment_update",
        msg_id=0
    )

    # --- Проверка типа и удаление ---
    if isinstance(msg_payment_id, int):
        try:
            await bot.delete_message(chat_id, msg_payment_id)
        except Exception:
            pass
