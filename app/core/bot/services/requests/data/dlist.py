"""
Универсальная обёртка для работы с данными пользователя из таблицы Data.

Содержит функции manage_data_list для извлечения всех пар ключ–значение
и manage_data_clear для удаления всех записей конкретного пользователя.
"""

from typing import Any, Dict

from app.core.database.engine import async_session
from app.core.database.managers import DataManager


async def manage_data_list(
    tg_id: int,
    keep_keys: list[str] | None = None,
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

        if keep_keys is not None:
            # Оптимизированное удаление всех ключей, которых нет в списке
            await data_manager.clear_except_keys(tg_id, keep_keys)

        return await data_manager.dict_all(tg_id)


async def manage_data_clear(
    tg_id: int,
    keep_keys: list[str] | None = None,
) -> bool:
    """
    Удаляет записи пользователя.

    Если keep_keys передан, удаляет все записи, ключей которых нет в списке.

    Args:
        tg_id (int): ID пользователя.
        keep_keys (list[str] | None): Список ключей, которые не удаляются.
            Если None, удаляются все записи.

    Returns:
        bool: True, если удаление прошло успешно, иначе False.
    """
    async with async_session() as session:
        data_manager = DataManager(session)

        if keep_keys is None:
            # Удаляем все записи
            return await data_manager.clear_all(tg_id)
        else:
            # Оптимизированное удаление всех ключей, которых нет в списке
            return await data_manager.clear_except_keys(tg_id, keep_keys)
