"""
Универсальная обёртка для обновления полей пользователя.

Содержит функцию manage_user_update для изменения информации
о пользователе в таблице User.
"""

from typing import Literal

from app.core.database.engine import async_session
from app.core.database.managers import UserManager


async def manage_user_update(
    tg_id: int,
    action: Literal["update_fullname"],
    fullname: str,
) -> bool:
    """
    Управляет обновлением полей пользователя.

    Args:
        tg_id (int): Telegram ID пользователя.
        action (Literal): Действие для выполнения.
            - "update_fullname": обновить полное имя пользователя.
        fullname (str): Новое значение полного имени пользователя.

    Returns:
        bool: True, если обновление прошло успешно, иначе False.
    """
    async with async_session() as session:
        manager = UserManager(session)

        if action == "update_fullname":
            return await manager.update_fullname(tg_id, fullname)

        raise ValueError(f"Неизвестное действие: {action!r}")
