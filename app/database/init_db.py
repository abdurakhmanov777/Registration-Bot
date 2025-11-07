from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from .engine import engine
from .models.base import Base


async def async_main() -> None:
    """Инициализация базы данных — создаёт таблицы при их отсутствии."""
    try:
        async with engine.begin() as conn:
            # Base уже знает все модели через наследование
            await conn.run_sync(Base.metadata.create_all)
        logger.debug("База данных инициализирована")
    except SQLAlchemyError as error:
        logger.error(f"Ошибка при инициализации базы данных: {error}")
        raise
