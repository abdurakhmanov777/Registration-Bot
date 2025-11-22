"""
Универсальная обёртка для работы с данными пользователя из таблицы Data.

Содержит функции manage_data_list для извлечения всех пар ключ–значение
и manage_data_clear для удаления всех записей конкретного пользователя.
"""

from typing import Any, Dict, Sequence

from app.core.database.engine import async_session
from app.core.database.managers import DataManager
from app.core.database.models import Data


async def manage_data_list(
    tg_id: int,
) -> Dict[str, Any]:
    """
    Получает все записи (ключ–значение) для конкретного пользователя.

    Args:
        tg_id (int): ID пользователя.

    Returns:
        Sequence[Data]: Список объектов Data, принадлежащих пользователю.
            Пустой список, если записей нет или произошла ошибка.
    """
    async with async_session() as session:
        data_manager: Any = DataManager(session)
        return await data_manager.dict_all(tg_id)


async def manage_data_clear(
    tg_id: int,
) -> bool:
    """
    Удаляет все записи пользователя.

    Args:
        tg_id (int): ID пользователя.

    Returns:
        bool: True, если удаление прошло успешно, иначе False.
    """
    async with async_session() as session:
        data_manager = DataManager(session)
        return await data_manager.clear_all(tg_id)
