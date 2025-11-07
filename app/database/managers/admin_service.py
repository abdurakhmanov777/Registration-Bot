from typing import Tuple

from sqlalchemy import Result, delete, select, update
from sqlalchemy.exc import SQLAlchemyError

from app.database.engine import async_session
from app.database.models.admin import Admin


class AdminService:
    """Менеджер для работы с таблицей Admin."""

    @staticmethod
    async def get_by_tg_id(
        tg_id: int
    ) -> Admin | None:
        """Получить админа по Telegram ID."""
        async with async_session() as session:
            try:
                result: Result[Tuple[Admin]] = await session.execute(
                    select(Admin).where(Admin.tg_id == tg_id)
                )
                return result.scalars().first()
            except SQLAlchemyError as error:
                raise RuntimeError(f"Ошибка при получении Admin: {error}")

    @staticmethod
    async def create(
        tg_id: int,
        msg_id: int,
        state: str = "1",
        name: str | None = None,
        lang: str = "ru",
        text: str = "Нет текста",
        entities: str = "None",
    ) -> Admin:
        """Создать нового администратора."""
        async with async_session() as session:
            admin = Admin(
                tg_id=tg_id,
                msg_id=msg_id,
                state=state,
                name=name,
                lang=lang,
                text=text,
                entities=entities,
            )
            session.add(admin)
            try:
                await session.commit()
                await session.refresh(admin)
                return admin
            except SQLAlchemyError as error:
                await session.rollback()
                raise RuntimeError(f"Ошибка при создании Admin: {error}")

    @staticmethod
    async def update_state(tg_id: int, state: str) -> None:
        """Обновить состояние администратора."""
        async with async_session() as session:
            try:
                await session.execute(
                    update(Admin).where(
                        Admin.tg_id == tg_id
                    ).values(state=state)
                )
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise RuntimeError(f"Ошибка при обновлении Admin: {error}")

    @staticmethod
    async def delete(tg_id: int) -> None:
        """Удалить администратора по Telegram ID."""
        async with async_session() as session:
            try:
                await session.execute(delete(
                    Admin
                ).where(Admin.tg_id == tg_id))
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise RuntimeError(f"Ошибка при удалении Admin: {error}")
