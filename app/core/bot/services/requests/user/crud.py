"""
Универсальная обёртка для работы с таблицей пользователей.

Содержит функцию manage_user для выполнения основных операций:
создание, получение, обновление и удаление пользователя.
"""

from typing import Any, Literal, Optional, Union

from app.core.database.engine import async_session
from app.core.database.managers import UserManager
from app.core.database.models import User


async def manage_user(
    tg_id: int,
    action: Literal[
        "get",
        "msg_update",
        "msg_payment_update",
        "get_or_create",
        "create",
        "update",
        "delete"
    ] = "get",
    lang: str = "ru",
    **fields: Any,
) -> Union[User, bool, None, int]:
    """
    Управляет CRUD-операциями пользователя.

    Выполняет создание, получение, обновление или удаление пользователя
    в базе данных через менеджер UserManager.

    Args:
        tg_id (int): Telegram ID пользователя.
        action (Literal): Действие для выполнения.
            - "get": получить пользователя;
            - "get_or_create": получить или создать пользователя;
            - "msg_update": обновить msg_id и получить старый
            - "create": создать пользователя;
            - "update": обновить поля пользователя;
            - "delete": удалить пользователя.
        lang (str):
            Язык пользователя (для create/update, по умолчанию "ru").
        msg_id (int):
            ID последнего сообщения (для create/update, по умолчанию 0).
        state (Optional[str]):
            Статус пользователя (для update).
        **fields (Any):
            Дополнительные поля для обновления (для update).

    Returns:
        Union[User, bool, None]:
            - User: объект пользователя для get, get_or_create,
                create или update;
            - bool: результат удаления для delete;
            - None: если get не нашёл пользователя.
    """
    async with async_session() as session:
        manager = UserManager(session)

        if action == "get":
            return await manager.get(tg_id)

        elif action == "get_or_create":
            return await manager.get_or_create(
                tg_id,
                lang=lang,
                msg_id=fields.get("msg_id", 0),
            )
        elif action == "msg_update":
            return await manager.msg_update(
                tg_id,
                msg_id=fields.get("msg_id", 0),
            )
        elif action == "msg_payment_update":
            print(1)
            return await manager.msg_payment_update(
                tg_id,
                msg_id=fields.get("msg_payment_id", 0),
            )
        elif action == "create":
            return await manager.create(
                tg_id=tg_id,
                lang=lang,
                msg_id=fields.get("msg_id", 0),
            )

        elif action == "update":
            # Обновляем все переданные поля через fields, исключая None
            update_fields: dict[str, Any] = {
                k: v for k, v in fields.items() if v is not None
            }
            if not update_fields:
                raise ValueError("Нет полей для обновления")
            return await manager.update(tg_id, **update_fields)

        elif action == "delete":
            return await manager.delete(tg_id)

        raise ValueError(f"Неизвестное действие: {action!r}")
