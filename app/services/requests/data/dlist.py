"""
Универсальная обёртка для получения всех записей пользователя из таблицы Data.

Содержит функцию manage_data_list для извлечения всех пар ключ–значение
конкретного пользователя.
"""

from typing import Sequence

from app.core.database.engine import async_session
from app.core.database.managers import DataManager
from app.core.database.models import Data


async def manage_data_list(
    user_id: int,
) -> Sequence[Data]:
    """
    Получает все записи (ключ–значение) для конкретного пользователя.

    Args:
        user_id (int): ID пользователя.

    Returns:
        Sequence[Data]: Список объектов Data, принадлежащих пользователю.
            Пустой список, если записей нет или произошла ошибка.
    """
    async with async_session() as session:
        data_manager = DataManager(session)
        return await data_manager.list_all(user_id)
