"""
Модуль инициализации базы данных.
Создаёт таблицы при их отсутствии.
"""

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from .engine import engine
from .models import Base


async def init_db() -> None:
    """
    Инициализация базы данных.

    Создаёт все таблицы, если их ещё нет, используя
    метаданные всех моделей, наследующих Base.
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
