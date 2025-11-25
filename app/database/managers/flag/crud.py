"""
CRUD-операции для таблицы Flag.

Содержит методы для создания, получения, обновления и
удаления флагов.
"""

from typing import Optional, Tuple

from loguru import logger
from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import Flag

from .base import FlagManagerBase


class FlagCRUD(FlagManagerBase):
    """Класс для выполнения CRUD-операций с флагами."""

    async def get(
        self,
        name: str,
    ) -> Optional[Flag]:
        """
        Получить флаг по имени.

        Args:
            name (str): Имя флага.

        Returns:
            Optional[Flag]: Объект Flag или None, если флаг
                не найден.
        """
        try:
            result: Result[Tuple[Flag]] = await self.session.execute(
                select(Flag).where(Flag.name == name)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            # Выводим сообщение об ошибке при получении флага
            logger.error(f"Ошибка при получении флага: {e}")
            return None

    async def create(
        self,
        name: str,
        value: bool = False,
    ) -> Flag:
        """
        Создать новый флаг.

        Args:
            name (str): Имя флага.
            value (bool): Значение флага (по умолчанию False).

        Returns:
            Flag: Созданный объект флага.
        """
        flag = Flag(name=name, value=value)

        # Добавляем флаг в сессию
        self.session.add(flag)
        await self.session.commit()
        await self.session.refresh(flag)
        return flag

    async def update(
        self,
        name: str,
        value: bool,
    ) -> bool:
        """
        Обновить значение флага.

        Args:
            name (str): Имя флага.
            value (bool): Новое значение флага.

        Returns:
            bool: True, если обновление прошло успешно, иначе False.
        """
        flag: Optional[Flag] = await self.get(name)
        if not flag:
            # Флаг не найден
            return False

        flag.value = value
        await self.session.commit()
        return True

    async def delete(
        self,
        name: str,
    ) -> bool:
        """
        Удалить флаг по имени.

        Args:
            name (str): Имя флага.

        Returns:
            bool: True, если удаление прошло успешно, иначе False.
        """
        flag: Optional[Flag] = await self.get(name)
        if not flag:
            # Флаг не найден
            return False

        await self.session.delete(flag)
        await self.session.commit()
        return True
