"""
Базовый класс менеджера администраторов.

Содержит общий функционал для работы с таблицей администраторов
через асинхронную сессию SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class AdminManagerBase:
    """
    Базовый менеджер администраторов.

    Атрибуты:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
    """

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
