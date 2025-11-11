"""
CRUD-операции для работы с таблицей администраторов.

Содержит методы для создания, получения и удаления администраторов
в базе данных.
"""

from typing import Optional, Tuple

from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.database.models import Admin

from .base import AdminManagerBase


class AdminCRUD(AdminManagerBase):
    """Класс для выполнения CRUD-операций с администраторами."""

    async def get(
        self,
        tg_id: int,
    ) -> Optional[Admin]:
        """
        Получить администратора по Telegram ID.

        Args:
            tg_id (int): Telegram ID администратора.

        Returns:
            Optional[Admin]: Объект администратора или None.
        """
        try:
            result: Result[Tuple[Admin]] = await self.session.execute(
                select(Admin).where(Admin.tg_id == tg_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            # Логируем ошибку при получении администратора
            print(f"Ошибка при получении администратора: {e}")
            return None

    async def create(
        self,
        tg_id: int,
        name: Optional[str] = None,
        lang: str = "ru",
        text: str = "Нет текста",
        entities: str = "None",
        msg_id: int = 0,
    ) -> Admin:
        """
        Создать нового администратора.

        Args:
            tg_id (int): Telegram ID администратора.
            name (Optional[str]): Имя администратора.
            lang (str): Язык администратора.
            text (str): Текст сообщения администратора.
            entities (str): Сущности сообщения.
            msg_id (int): ID сообщения.

        Returns:
            Admin: Созданный объект администратора.
        """
        admin = Admin(
            tg_id=tg_id,
            name=name,
            lang=lang,
            text=text,
            entities=entities,
            msg_id=msg_id,
            state="1",
        )
        # Добавляем администратора в сессию и сохраняем изменения
        self.session.add(admin)
        await self.session.commit()
        await self.session.refresh(admin)
        return admin

    async def delete(
        self,
        tg_id: int,
    ) -> bool:
        """
        Удалить администратора по Telegram ID.

        Args:
            tg_id (int): Telegram ID администратора.

        Returns:
            bool: True, если удаление успешно, иначе False.
        """
        admin: Optional[Admin] = await self.get(tg_id)
        if not admin:
            # Администратор с указанным ID не найден
            return False

        await self.session.delete(admin)
        await self.session.commit()
        return True
