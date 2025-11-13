"""
Универсальная обёртка для работы с таблицей Data.

Содержит функцию manage_data_crud для выполнения CRUD-операций:
создание, получение, обновление и удаление пользовательских данных.
"""

from typing import Literal, Optional, Union

from app.core.database.engine import async_session
from app.core.database.managers import DataManager
from app.core.database.models import Data


async def manage_data_crud(
    user_id: int,
    action: Literal["get", "create", "update", "delete"],
    key: str,
    value: Optional[str] = None,
) -> Union[Data, bool, None]:
    """
    Управляет CRUD-операциями с пользовательскими данными.

    Args:
        user_id (int): ID пользователя.
        action (Literal["get", "create", "update", "delete"]): Действие для
            выполнения.
            - "get": получить значение по ключу;
            - "create": создать новую запись;
            - "update": обновить существующую запись;
            - "delete": удалить запись.
        key (str): Ключ данных.
        value (Optional[str]): Значение данных (для create/update).

    Returns:
        Union[Data, bool, None]:
            - Data: объект данных для get/create;
            - bool: результат операции update/delete;
            - None: если запись не найдена при get.

    Raises:
        ValueError: Если action неизвестен или value не передан для
            create/update.
    """
    async with async_session() as session:
        data_manager = DataManager(session)

        if action == "get":
            return await data_manager.get(user_id, key)

        elif action in ("create", "update"):
            if value is None:
                raise ValueError(
                    f'Для {action} необходимо передать значение value.'
                )
            if action == "create":
                return await data_manager.create(user_id, key, value)
            return await data_manager.update(user_id, key, value)

        elif action == "delete":
            return await data_manager.delete(user_id, key)

        raise ValueError(f"Неизвестное действие: {action!r}")
