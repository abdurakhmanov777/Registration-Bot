"""
Универсальная обёртка для работы со стеком состояний пользователя.

Содержит функцию manage_user_state для выполнения основных операций со
стеком состояний: push, pop, peek, peekpush, popeek, clear и get_state.
"""

from typing import List, Literal, Optional, Union

from app.core.database.engine import async_session
from app.core.database.managers import UserManager


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
) -> Union[bool, str, list[str], None]:
    """
    Управляет стеком состояний пользователя.

    Args:
        tg_id (int): Telegram ID пользователя.
        action (Literal): Действие для выполнения со стеком состояния.
            Доступные варианты:
            - "push": добавить новое состояние;
            - "pop": удалить последнее состояние;
            - "peek": посмотреть текущее состояние;
            - "peekpush": вернуть текущее и добавить новое состояние;
            - "popeek": удалить последнее и вернуть предыдущее;
            - "clear": очистить стек состояний;
            - "get_state": вернуть весь стек состояний.
        new_state (Optional[str]): Новое состояние для добавления.
            Обязателен для действий "push" и "peekpush".

    Returns:
        Union[bool, str, list[str], None]: Результат выполнения действия.
            - str: текущее состояние;
            - list[str]: весь стек состояний;
            - bool: успех операции clear;
            - None: если стек пустой или отсутствует значение.
    """
    async with async_session() as session:
        manager = UserManager(session)

        if action in ("push", "peekpush") and new_state is None:
            raise ValueError(
                f"Для действия '{action}' необходимо указать new_state."
            )

        if action == "push":
            assert new_state is not None
            return await manager.push_state(tg_id, new_state)

        if action == "peekpush":
            assert new_state is not None
            current_state: Optional[str] = await manager.peek_state(tg_id)
            await manager.push_state(tg_id, new_state)
            return current_state

        if action == "pop":
            return await manager.pop_state(tg_id)

        if action == "peek":
            return await manager.peek_state(tg_id)

        if action == "popeek":
            last_state: str | None = await manager.pop_state(tg_id)
            return await manager.peek_state(tg_id) or last_state

        if action == "clear":
            await manager.clear_state(tg_id)
            return True

        if action == "get_state":
            states: List[str] = await manager.get_state(tg_id)
            return states or ["1"]

        raise ValueError(f"Неизвестное действие: {action!r}")
