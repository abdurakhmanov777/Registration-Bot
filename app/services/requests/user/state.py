"""
Универсальная обёртка для управления стеком состояний пользователя
с автоматическим созданием сессии и менеджера.
"""

from typing import Any, Literal, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.engine import async_session
from app.core.database.managers import UserManager
from app.core.database.models.user import User


async def manage_user_state(
    tg_id: int,
    action: Literal[
        "push",
        "pop",
        "peek",
        "peekpush",
        "popeek",
        "clear",
        "get_state",
    ] = "peek",
    new_state: Optional[str] = None,
) -> Optional[Any]:
    """
    Выполняет указанное действие над стеком состояний пользователя.

    Создаёт собственную сессию и менеджер UserManager, поэтому их
    не нужно передавать явно.

    Args:
        tg_id (int): Telegram ID пользователя.
        action (Literal): Действие над стеком состояний.
            Поддерживаемые значения: "push", "pop", "peek",
            "peekpush", "popeek", "clear", "get_state".
        new_state (Optional[str]): Новое состояние для добавления
            (используется только для "push" и "peekpush").

    Returns:
        Optional[Any]:
            - Для "push":
                True, если добавлено успешно, иначе False.
            - Для "pop", "peek", "peekpush", "popeek":
                Строка состояния или None.
            - Для "get_state":
                Список всех состояний.
            - Для "clear":
                True.
    Raises:
        ValueError: Если указано неизвестное действие или не задано
            новое состояние для операций "push"/"peekpush".
    """
    async with async_session() as session:
        manager = UserManager(session)
        print(f"[DEBUG] (оболочка) UserManager session id: {id(session)}")
        if action == "push":
            if new_state is None:
                raise ValueError(
                    "Для действия 'push' необходимо указать new_state."
                )
            return await manager.push_state(tg_id, new_state)

        elif action == "pop":
            return await manager.pop_state(tg_id)

        elif action == "peek":
            return await manager.peek_state(tg_id)

        elif action == "peekpush":
            if new_state is None:
                raise ValueError(
                    "Для действия 'peekpush' необходимо указать new_state."
                )
            current: Optional[str] = await manager.peek_state(tg_id)
            await manager.push_state(tg_id, new_state)
            return current

        elif action == "popeek":
            last: Optional[str] = await manager.pop_state(tg_id)
            prev: Optional[str] = await manager.peek_state(tg_id)
            return prev or last

        elif action == "clear":
            # Сброс состояния до базового
            await manager.push_state(tg_id, "1")
            while True:
                state: Optional[str] = await manager.pop_state(tg_id)
                if not state or state == "1":
                    break
            return True

        elif action == "get_state":
            # Получаем стек состояний как список
            states: list[str] = await manager.get_state(tg_id)

            # Если стек пустой, возвращаем ["1"]
            if not states:
                return ["1"]

            return states

        else:
            raise ValueError(f"Неизвестное действие: {action!r}")
