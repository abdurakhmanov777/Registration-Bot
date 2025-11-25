"""
Базовый класс менеджера пользователей.

Содержит общую функциональность для работы с таблицей User
через асинхронную сессию SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class UserManagerBase:
    """Базовый класс для работы с таблицей User."""

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Инициализация менеджера пользователей.

        Args:
            session (AsyncSession): Асинхронная сессия для работы
                с базой данных.
        """
        # Сохраняем сессию для дальнейшей работы с БД
        self.session: AsyncSession = session
