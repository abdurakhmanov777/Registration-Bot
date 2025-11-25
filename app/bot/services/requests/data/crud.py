"""
Универсальная обёртка для работы с таблицей Data.

Содержит функцию manage_data для выполнения CRUD-операций:
создание, получение, обновление и удаление пользовательских данных.
"""

from typing import Literal, Optional

from app.database.engine import async_session
from app.database.managers import DataManager
from app.database.models.data import Data


async def manage_data(
    tg_id: int,
    action: Literal["get", "create_or_update", "delete"],
    key: str,
    value: Optional[str] = None,
) -> Optional[str]:
    """
    Выполняет CRUD-операции с пользовательскими данными и возвращает результат
    в виде строки.

    Args:
        tg_id (int): ID пользователя.
        action (Literal["get", "create_or_update", "delete"]): Действие:
            - "get": получить запись по ключу;
            - "create_or_update": создать новую запись или обновить существующую;
            - "delete": удалить запись.
        key (str): Ключ данных.
        value (Optional[str]): Значение данных (для create_or_update).

    Returns:
        Optional[str]: Строковое значение данных для get/create_or_update,
        "True"/"False" для delete или None, если запись не найдена при get.

    Raises:
        ValueError: Если action неизвестен или value не передан для
            create_or_update.
    """
    async with async_session() as session:
        data_manager = DataManager(session)

        if action == "get":
            data: Data | None = await data_manager.get(tg_id, key)
            return data.value if data else None

        elif action == "create_or_update":
            if value is None:
                raise ValueError(
                    'Для create_or_update необходимо передать значение value.'
                )
            data = await data_manager.create_or_update(tg_id, key, value)
            return data.value

        elif action == "delete":
            result: bool = await data_manager.delete(tg_id, key)
            return str(result)

        raise ValueError(f"Неизвестное действие: {action!r}")
