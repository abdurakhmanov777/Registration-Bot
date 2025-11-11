"""
Универсальная обёртка для работы с таблицей пользователей.

Содержит функцию manage_user для выполнения основных операций:
создание, получение и удаление пользователя.
"""

from typing import Literal, Optional, Union

from app.core.database.engine import async_session
from app.core.database.managers import UserManager
from app.core.database.models import User


async def manage_user(
    tg_id: int,
    action: Literal["get", "create", "delete"] = "get",
    fullname: Optional[str] = None,
    group: Optional[str] = None,
    lang: str = "ru",
    msg_id: int = 0,
    column: Optional[int] = None,
) -> Union[User, bool, None]:
    """
    Управляет CRUD-операциями пользователя.

    Args:
        tg_id (int): Telegram ID пользователя.
        action (Literal): Действие для выполнения.
            - "get": получить пользователя;
            - "create": создать пользователя (если не существует);
            - "delete": удалить пользователя.
        fullname (Optional[str]): Полное имя пользователя (для create).
        group (Optional[str]): Группа пользователя (для create).
        lang (str): Язык пользователя (для create, по умолчанию "ru").
        msg_id (int): ID последнего сообщения (для create, по умолчанию 0).
        column (Optional[int]): Дополнительный параметр column (для create).

    Returns:
        Union[User, bool, None]:
            - User: объект пользователя для get/create;
            - bool: результат удаления для delete;
            - None: если get не нашёл пользователя.
    """
    async with async_session() as session:
        manager = UserManager(session)

        if action == "get":
            return await manager.get(tg_id)

        elif action == "create":
            return await manager.get_or_create(
                tg_id=tg_id,
                fullname=fullname,
                group=group,
                lang=lang,
                msg_id=msg_id,
                column=column,
            )

        elif action == "delete":
            return await manager.delete(tg_id)

        raise ValueError(f"Неизвестное действие: {action!r}")
