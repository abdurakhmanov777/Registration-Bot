"""
Базовый middleware для обработки событий Aiogram.
"""

from typing import Any, Awaitable, Callable, Dict, Literal, Optional, Set

from aiogram import BaseMiddleware

from app.core.bot.middleware.user.fsm import clear_fsm_user
from app.core.bot.services.logger import log_error
from app.core.database import Admin, User

from . import utils
from .user.process import user_before


class MwBase(BaseMiddleware):
    """Базовый middleware для обработки событий Aiogram."""

    def __init__(
        self,
        delete_event: bool = False,
        role: Literal["user", "admin"] = "user",
        allowed_types: Optional[Set[str]] = None,
        **extra_data: Any,
    ) -> None:
        """
        Инициализация middleware.

        Parameters
        ----------
        delete_event : bool
            Флаг удаления исходного сообщения после обработки.
        role : Literal["user", "admin"]
            Роль для обработки (user или admin).
        allowed_types : Optional[Set[str]]
            Разрешённые типы сообщений.
        **extra_data : Any
            Дополнительные данные для передачи в handler.
        """
        self.delete_event: bool = delete_event
        self.role: Literal["user", "admin"] = role
        self.extra_data: Dict[str, Any] = extra_data

        self.allowed: Set[str] = {"text"}
        if allowed_types:
            self.allowed.update(allowed_types)

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Optional[Any] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Обрабатывает событие и вызывает handler.

        Parameters
        ----------
        handler : Callable[[Any, Dict[str, Any]], Awaitable[Any]]
            Асинхронная функция-обработчик события.
        event : Optional[Any]
            Событие пользователя.
        data : Optional[Dict[str, Any]]
            Словарь данных для передачи в handler.

        Returns
        -------
        Any
            Результат работы handler или None.
        """
        if event is None or not getattr(event, "from_user", None):
            return None

        if not await utils.check_type(event, self.allowed):
            return None

        data = data or {}
        data.update(self.extra_data)

        user: Optional[User] = None
        db: Optional[Dict[str, str]] = None
        msg_id: int = 0

        if self.role == "user":
            user, db, msg_id = await user_before(data, event)
        else:
            # Логика для админов будет добавлена позже
            pass

        try:
            result: Any = await handler(event, data)
            await utils.remove_event(event, self.delete_event)

        except Exception as error:
            await log_error(event, error=error)
            return None

        if self.role == "user":
            chat_id: Any | None = await utils.extract_attribute(
                event, "chat.id"
            )
            if chat_id is not None:
                await utils.remove_old_msg(event, chat_id, msg_id)

            await utils.update_db(
                tg_id=event.from_user.id,
                bot_id=event.bot.id,
                user=user,
                data=db,
            )

        else:
            # Логика для админов будет добавлена позже
            pass
        
        return result
