from typing import Tuple

from sqlalchemy import Result, delete, select, update
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import User, async_session


class UserService:
    """Менеджер для работы с таблицей User."""

    @staticmethod
    async def get_by_tg_id(tg_id: int) -> User | None:
        """Получить пользователя по Telegram ID."""
        async with async_session() as session:
            try:
                result: Result[Tuple[User]] = await session.execute(
                    select(User).where(User.tg_id == tg_id)
                )
                return result.scalars().first()
            except SQLAlchemyError as error:
                raise RuntimeError(f"Ошибка при получении User: {error}")

    @staticmethod
    async def create(
        tg_id: int,
        msg_id: int,
        state: str = "1",
        fullname: str | None = None,
        group: str | None = None,
        lang: str = "ru",
    ) -> User:
        """Создать нового пользователя."""
        async with async_session() as session:
            user = User(
                tg_id=tg_id,
                msg_id=msg_id,
                state=state,
                fullname=fullname,
                group=group,
                lang=lang,
            )
            session.add(user)
            try:
                await session.commit()
                await session.refresh(user)
                return user
            except SQLAlchemyError as error:
                await session.rollback()
                raise RuntimeError(f"Ошибка при создании User: {error}")

    @staticmethod
    async def update_state(tg_id: int, state: str) -> None:
        """Обновить состояние пользователя."""
        async with async_session() as session:
            try:
                await session.execute(
                    update(User).where(User.tg_id == tg_id).values(state=state)
                )
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise RuntimeError(f"Ошибка при обновлении User: {error}")

    @staticmethod
    async def delete(
        tg_id: int
    ) -> None:
        """Удалить пользователя по Telegram ID."""
        async with async_session() as session:
            try:
                await session.execute(delete(User).where(User.tg_id == tg_id))
                await session.commit()
            except SQLAlchemyError as error:
                await session.rollback()
                raise RuntimeError(f"Ошибка при удалении User: {error}")
