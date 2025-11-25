"""
Модуль инициализации базы данных.

Создает таблицы при их отсутствии с использованием метаданных моделей.
"""

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from .engine import engine
from .models import Base


async def init_db() -> None:
    """Инициализация базы данных.

    Создает все таблицы, если их ещё нет, используя метаданные всех
    моделей, наследующих Base.

    Raises:
        SQLAlchemyError: Ошибка при создании таблиц базы данных.
    """
    try:
        async with engine.begin() as conn:
            # Base.metadata содержит информацию обо всех моделях
            await conn.run_sync(Base.metadata.create_all)
        logger.debug("База данных инициализирована")
    except SQLAlchemyError as error:
        logger.error(
            f"Ошибка при инициализации базы данных: {error}"
        )
        raise
