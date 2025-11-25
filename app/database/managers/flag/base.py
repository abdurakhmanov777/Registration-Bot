"""
Базовый класс менеджера флагов.

Содержит общую функциональность для работы с таблицей Flag
через асинхронную сессию SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class FlagManagerBase:
    """Базовый менеджер для работы с таблицей Flag."""

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Инициализация менеджера флагов.

        Args:
            session (AsyncSession): Асинхронная сессия для работы
                с базой данных.
        """
        # Сохраняем сессию для дальнейшей работы с БД
        self.session: AsyncSession = session
