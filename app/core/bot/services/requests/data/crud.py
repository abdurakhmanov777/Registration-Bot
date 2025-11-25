"""
Универсальная обёртка для работы с таблицей Data.

Модуль содержит функцию manage_data для выполнения CRUD-операций:
создание, получение, обновление и удаление пользовательских данных
по Telegram ID пользователя.
"""

from typing import Literal, Optional

from app.core.database.engine import async_session
from app.core.database.managers import DataManager
from app.core.database.models.data import Data


async def manage_data(
    tg_id: int,
    action: Literal["get", "create_or_update", "delete"],
    key: str,
    value: Optional[str] = None,
) -> Optional[str]:
    """Выполняет CRUD-операции с пользовательскими данными.

    Оборачивает методы DataManager для работы с таблицей Data.
    Возвращает строковое значение данных для get/create_or_update,
    "True"/"False" для delete или None, если запись не найдена.

    Args:
        tg_id (int): Telegram ID пользователя.
        action (Literal["get", "create_or_update", "delete"]): Действие:
            - "get": получить запись по ключу;
            - "create_or_update": создать новую запись или обновить существующую;
            - "delete": удалить запись.
        key (str): Ключ данных.
        value (Optional[str]): Значение данных для create_or_update.

    Returns:
        Optional[str]: Строковое значение данных, "True"/"False" для delete
        или None, если запись не найдена.

    Raises:
        ValueError: Если action неизвестен или value не передан для
            create_or_update.
    """
    async with async_session() as session:
        data_manager = DataManager(session)

        if action == "get":
            data: Optional[Data] = await data_manager.get(tg_id, key)
            return data.value if data else None

        if action == "create_or_update":
            if value is None:
                raise ValueError(
                    "Для create_or_update необходимо передать значение value."
                )
            data: Optional[Data] = await data_manager.create_or_update(
                tg_id, key, value
            )
            return data.value if data else None

        if action == "delete":
            result: bool = await data_manager.delete(tg_id, key)
            return str(result)

        raise ValueError(f"Неизвестное действие: {action!r}")
