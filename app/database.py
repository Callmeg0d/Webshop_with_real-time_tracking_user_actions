from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

if settings.MODE == "TEST":
    DATABASE_URL = settings.TEST_DATABASE_URL
    DATABASE_PARAMS = {"poolclass": NullPool}
else:
    DATABASE_URL = settings.DATABASE_URL
    DATABASE_PARAMS = {}

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)
# Создание движка (небольших транзакций)
async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass