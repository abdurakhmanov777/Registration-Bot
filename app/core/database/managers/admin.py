from typing import List, Optional, Tuple

from sqlalchemy import Result, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.models import Admin


class AdminManager:
    """Менеджер для работы с таблицей администраторов.

    Позволяет выполнять CRUD операции и управлять стеком состояний
    администратора.
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
        tg_id: int
    ) -> Optional[Admin]:
        """
        Получить администратора по tg_id.

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
            # Логирование ошибки получения администратора
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
            lang (str): Язык (по умолчанию "ru").
            text (str): Текст сообщения.
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
            state="1",  # начальный стек
        )
        self.session.add(admin)
        await self.session.commit()
        await self.session.refresh(admin)
        return admin

    async def push_state(
        self,
        tg_id: int,
        new_state: str
    ) -> bool:
        """
        Добавить состояние в стек state администратора.

        Args:
            tg_id (int): Telegram ID администратора.
            new_state (str): Новое состояние для добавления.

        Returns:
            bool: True, если успешно, иначе False.
        """
        admin: Optional[Admin] = await self.get(tg_id)
        if not admin:
            return False

        stack: List[str] = admin.state.split(",") if admin.state else []
        stack.append(new_state)
        admin.state = ",".join(stack)
        await self.session.commit()
        return True

    async def pop_state(
        self,
        tg_id: int
    ) -> Optional[str]:
        """
        Извлечь последнее состояние из стека state.

        Args:
            tg_id (int): Telegram ID администратора.

        Returns:
            Optional[str]: Последнее состояние или None, если стек пуст.
        """
        admin: Optional[Admin] = await self.get(tg_id)
        if not admin:
            return None

        stack: List[str] = admin.state.split(",") if admin.state else []
        if not stack:
            return None

        last_state: str = stack.pop()
        admin.state = ",".join(stack)
        await self.session.commit()
        return last_state

    async def peek_state(
        self,
        tg_id: int
    ) -> Optional[str]:
        """
        Посмотреть последнее состояние в стеке без удаления.

        Args:
            tg_id (int): Telegram ID администратора.

        Returns:
            Optional[str]: Последнее состояние или None, если стек пуст.
        """
        admin: Optional[Admin] = await self.get(tg_id)
        if not admin:
            return None

        stack: List[str] = admin.state.split(",") if admin.state else []
        return stack[-1] if stack else None

    async def update_text(
        self,
        tg_id: int,
        new_text: str
    ) -> bool:
        """
        Обновить текст администратора.

        Args:
            tg_id (int): Telegram ID администратора.
            new_text (str): Новый текст.

        Returns:
            bool: True, если успешно, иначе False.
        """
        admin: Optional[Admin] = await self.get(tg_id)
        if not admin:
            return False

        admin.text = new_text
        await self.session.commit()
        return True

    async def delete(
        self,
        tg_id: int
    ) -> bool:
        """
        Удалить администратора из базы.

        Args:
            tg_id (int): Telegram ID администратора.

        Returns:
            bool: True, если удаление прошло успешно.
        """
        admin: Optional[Admin] = await self.get(tg_id)
        if not admin:
            return False

        await self.session.delete(admin)
        await self.session.commit()
        return True
