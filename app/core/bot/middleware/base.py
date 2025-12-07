"""
Модуль содержит базовый middleware для обработки событий Aiogram.

Middleware выполняет фильтрацию типов сообщений, подсчёт вызовов,
удаление событий, проверку роли пользователя, обновление данных FSM и БД,
а также удаление сообщений неподдерживаемых типов.
"""

from typing import Any, Awaitable, Callable, Dict, Literal, Optional, Set

from aiogram import BaseMiddleware
from aiogram.types import ContentType, Message

from app.core.bot.services.logger import log_error
from app.core.database import async_session
from app.core.database.managers import DataManager, UserManager
from app.core.database.models import User

from .refresh import refresh_fsm_data


class MwBase(BaseMiddleware):
    """
    Базовый middleware для обработки событий Aiogram.

    Middleware поддерживает подсчёт вызовов обработчика, удаление события,
    проверку роли пользователя, обновление локализации и данных FSM, а также
    фильтрацию неподдерживаемых типов сообщений.

    Parameters
    ----------
    delete_event : bool
        Удалять ли событие после обработки.
    role : Literal["user", "admin"]
        Роль пользователя, необходимая для выполнения обработчика.
    allowed_types : Optional[Set[str]]
        Набор допустимых типов сообщений.
    **extra_data : Any
        Дополнительные параметры, передаваемые в data для обработчика.
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
        self.extra_data: Dict[str, Any] = extra_data

        self.allowed_types: Set[str] = {ContentType.TEXT}
        if allowed_types:
            self.allowed_types.update(allowed_types)

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Optional[Any] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Основной метод вызова middleware.

        Проверяет корректность события, фильтрует по типу сообщения,
        обновляет FSM данные, выполняет обработчик, затем обновляет БД
        и при необходимости удаляет сообщение или событие.

        Parameters
        ----------
        handler : Callable
            Обработчик события.
        event : Optional[Any]
            Обрабатываемое событие (Message или CallbackQuery).
        data : Optional[Dict[str, Any]]
            Словарь данных, передаваемый обработчику.

        Returns
        -------
        Any
            Возвращаемое значение обработчика или None при ошибке.
        """
        if event is None or not event.from_user:
            return

        # Фильтрация неподдерживаемых типов сообщений.
        if isinstance(
            event,
            Message
        ) and event.content_type not in self.allowed_types:
            try:
                await event.delete()
            except BaseException:
                pass
            return None

        data = data or {}
        self.counter += 1

        data["counter"] = self.counter
        data.update(self.extra_data)
        user_db: User | None
        data_db: Dict[str, str] | None
        user_db, data_db = await refresh_fsm_data(
            data=data,
            event=event,
            role=self.role,
        )

        msg_id: int = user_db.msg_payment_id if user_db else 0

        try:
            result: Any = await handler(event, data)

            chat_id: int | None = None
            if isinstance(event, Message):
                chat_id = event.chat.id
            else:
                msg: Any | None = getattr(event, "message", None)
                if isinstance(msg, Message):
                    chat_id = msg.chat.id

            if chat_id is not None and msg_id:
                if event.bot is None:
                    return
                try:
                    await event.bot.delete_message(chat_id, msg_id)
                except Exception:
                    pass

            if user_db and data_db is not None:
                async with async_session() as session:
                    await UserManager(session).update_user(user_db)
                    await DataManager(session).update_all(
                        event.from_user.id,
                        data_db,
                    )

            if self.delete_event:
                try:
                    await event.delete()
                except BaseException:
                    pass

            return result

        except Exception as error:
            await log_error(event, error=error)
            return None
