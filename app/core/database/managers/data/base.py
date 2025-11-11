"""
Базовый класс менеджера данных.

Содержит общую функциональность для работы с таблицей Data
через асинхронную сессию SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class DataManagerBase:
    """Базовый менеджер для работы с таблицей Data."""

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Инициализация менеджера.

        Args:
            session (AsyncSession): Асинхронная сессия для работы с БД.
        """
        # Сохраняем сессию для дальнейшей работы с базой данных
        self.session: AsyncSession = session
