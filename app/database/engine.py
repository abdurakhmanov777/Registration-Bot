"""
Настройка асинхронного движка SQLAlchemy и сессий.

Создает асинхронный движок и фабрику сессий для работы
с базой данных.
"""

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from app.config import DB_URL

if not DB_URL:
    raise ValueError("Переменная окружения DB_URL не установлена")

# Создание асинхронного движка SQLAlchemy
engine: AsyncEngine = create_async_engine(
    DB_URL,
    pool_size=10,
    max_overflow=20,
    future=True,
)

# Фабрика асинхронных сессий для работы с базой данных
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
