from typing import AsyncGenerator, Callable

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.constants import HttpHeaders


def create_get_db(
    async_session_maker: async_sessionmaker[AsyncSession]
) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    """
    Фабричная функция для создания зависимости get_db.

    Args:
        async_session_maker: Фабрика сессий базы данных для конкретного сервиса
        
    Returns:
        Функция-зависимость get_db для FastAPI
    """
    async def get_db() -> AsyncGenerator[AsyncSession, None]:
        """
        Получает асинхронную сессию базы данных.

        Yields:
            AsyncSession: Асинхронная сессия базы данных
        """
        async with async_session_maker() as session:
            yield session
    
    return get_db


async def get_user_id(
    x_user_id: int = Header(..., alias=HttpHeaders.X_USER_ID.value)
) -> int:
    """
    Получает user_id из заголовка X-User-Id.

    Args:
        x_user_id: ID пользователя из заголовка

    Returns:
        int: ID пользователя

    Raises:
        HTTPException: Если заголовок отсутствует или невалиден
    """
    if not x_user_id or x_user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID"
        )
    return x_user_id

