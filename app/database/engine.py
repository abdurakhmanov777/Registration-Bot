from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from config import DB_URL

if not DB_URL:
    raise ValueError("Переменная окружения DB_URL не установлена")

engine: AsyncEngine = create_async_engine(DB_URL)
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, expire_on_commit=False
)
