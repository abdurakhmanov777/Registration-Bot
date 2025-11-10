"""
Менеджер для работы с таблицей ключ–значение пользователя.

Позволяет создавать, получать, обновлять и удалять пары ключ–значение.
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.models import Data


class DataManager:
    """Менеджер для взаимодействия с таблицей Data."""

    def __init__(
        self,
        session: AsyncSession
    ) -> None:
        """
        Инициализация менеджера.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
        """
        self.session: AsyncSession = session

    async def get(
        self,
        user_id: int,
        key: str
    ) -> Optional[Data]:
        """
        Получить запись по ключу для конкретного пользователя.

        Args:
            user_id (int): Идентификатор пользователя.
            key (str): Ключ записи.

        Returns:
            Optional[Data]: Объект Data или None, если не найден.
        """
        try:
            result: Result[Tuple[Data]] = await self.session.execute(
                select(Data).where(
                    Data.user_id == user_id,
                    Data.key == key
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            print(f"Ошибка при получении данных: {e}")
            return None

    async def create(
        self,
        user_id: int,
        key: str,
        value: str
    ) -> Data:
        """
        Создать новую пару ключ–значение.

        Args:
            user_id (int): Идентификатор пользователя.
            key (str): Ключ.
            value (str): Значение.

        Returns:
            Data: Созданный объект Data.
        """
        data = Data(
            user_id=user_id,
            key=key,
            value=value
        )
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)
        return data

    async def update(
        self,
        user_id: int,
        key: str,
        value: str
    ) -> bool:
        """
        Обновить значение существующего ключа.

        Args:
            user_id (int): Идентификатор пользователя.
            key (str): Ключ.
            value (str): Новое значение.

        Returns:
            bool: True, если обновление успешно, иначе False.
        """
        data: Optional[Data] = await self.get(user_id, key)
        if not data:
            return False

        data.value = value
        await self.session.commit()
        return True

    async def delete(
        self,
        user_id: int,
        key: str
    ) -> bool:
        """
        Удалить пару ключ–значение пользователя.

        Args:
            user_id (int): Идентификатор пользователя.
            key (str): Ключ.

        Returns:
            bool: True, если удаление успешно, иначе False.
        """
        data: Optional[Data] = await self.get(user_id, key)
        if not data:
            return False

        await self.session.delete(data)
        await self.session.commit()
        return True

    async def list_all(
        self,
        user_id: int
    ) -> Sequence[Data]:
        """
        Получить все пары ключ–значение для пользователя.

        Args:
            user_id (int): Идентификатор пользователя.

        Returns:
            Sequence[Data]: Последовательность объектов Data.
        """
        try:
            result: Result[Tuple[Data]] = await self.session.execute(
                select(Data).where(Data.user_id == user_id)
            )
            # scalars().all() возвращает Sequence[Data]
            return result.scalars().all()
        except SQLAlchemyError as e:
            print(f"Ошибка при получении списка данных: {e}")
            return []
