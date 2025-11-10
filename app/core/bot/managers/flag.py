from typing import Optional, Sequence, Tuple

from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.models import Flag


class FlagManager:
    """Менеджер для работы с таблицей флагов.

    Позволяет выполнять CRUD операции и получать все флаги.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация менеджера.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
        """
        self.session: AsyncSession = session

    async def get(
        self,
        name: str
    ) -> Optional[Flag]:
        """
        Получить флаг по имени.

        Args:
            name (str): Имя флага.

        Returns:
            Optional[Flag]: Объект флага или None, если не найден.
        """
        try:
            result: Result[Tuple[Flag]] = await self.session.execute(
                select(Flag).where(Flag.name == name)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            # Логирование ошибки получения флага
            print(f"Ошибка при получении флага: {e}")
            return None

    async def create(
        self,
        name: str,
        value: bool = False
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
        self.session.add(flag)
        await self.session.commit()
        await self.session.refresh(flag)
        return flag

    async def update(
        self,
        name: str,
        value: bool
    ) -> bool:
        """
        Обновить значение флага.

        Args:
            name (str): Имя флага.
            value (bool): Новое значение.

        Returns:
            bool: True, если обновление прошло успешно, иначе False.
        """
        flag: Optional[Flag] = await self.get(name)
        if not flag:
            return False

        flag.value = value
        await self.session.commit()
        return True

    async def delete(
        self,
        name: str
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
            return False

        await self.session.delete(flag)
        await self.session.commit()
        return True

    async def list_all(
        self
    ) -> Sequence[Flag]:
        """
        Получить список всех флагов.

        Returns:
            Sequence[Flag]: Все флаги в базе.
        """
        try:
            result: Result[Tuple[Flag]] = await self.session.execute(
                select(Flag)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            # Логирование ошибки получения списка флагов
            print(f"Ошибка при получении списка флагов: {e}")
            return []
