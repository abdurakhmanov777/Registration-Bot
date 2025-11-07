from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from app.database.models.admin import Admin
from app.database.models.user import User

from .engine import engine
from .models.base import Base


async def async_main() -> None:
    """Инициализация базы данных — создаёт все таблицы при их отсутствии."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.debug("База данных инициализирована")
    except SQLAlchemyError as error:
        logger.error(f"Ошибка при инициализации базы данных: {error}")
        raise
