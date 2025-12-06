from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import Depends, Request
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.container import Container
from app.database import async_session_maker
from app.domain.entities.users import UserItem
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.services.auth_service import AuthService
from app.services.category_service import CategoryService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.services.review_service import ReviewService
from app.services.user_service import UserService



container = Container()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Получает асинхронную сессию базы данных.

    Используется как зависимость для всех сервисов и репозиториев.
    Сессия автоматически закрывается после завершения запроса.

    Yields:
        AsyncSession: Асинхронная сессия базы данных
    """
    async with async_session_maker() as session:
        yield session


async def get_orders_service(
        db: AsyncSession = Depends(get_db)
) -> OrderService:
    """
    Получает сервис заказов через DI-контейнер.

    Args:
        db: Асинхронная сессия базы данных

    Returns:
        OrderService: Сервис для работы с заказами
    """
    return container.order_service(db=db)


async def get_products_service(
        db: AsyncSession = Depends(get_db)
) -> ProductService:
    """
    Получает сервис товаров через DI-контейнер
    Args:
        db: Асинхронная сессия базы данных

    Returns:
        ProductService: Сервис для работы с товарами
    """
    return container.product_service(db=db)


async def get_carts_service(
        db: AsyncSession = Depends(get_db)
) -> CartService:
    """
    Получает сервис корзины через DI-контейнер
    Args:
        db: Асинхронная сессия базы данных

    Returns:
        CartService: Сервис для работы с корзиной
    """
    return container.cart_service(db=db)


async def get_users_service(
        db: AsyncSession = Depends(get_db)
) -> UserService:
    """
    Получает сервис пользователей через DI-контейнер
    Args:
        db: Асинхронная сессия базы данных

    Returns:
        UserService: Сервис для работы с пользователями
    """
    return container.user_service(db=db)


async def get_auth_service(
        db: AsyncSession = Depends(get_db)
) -> AuthService:
    """
    Получает сервис аутентификации через DI-контейнер
    Args:
        db: Асинхронная сессия базы данных

    Returns:
        AuthService: Сервис для работы с аутентификацией и авторизацией
    """
    return container.authentication_service(db=db)


async def get_reviews_service(
        db: AsyncSession = Depends(get_db)
) -> ReviewService:
    """
    Получает сервис отзывов через DI-контейнер
    Args:
        db: Асинхронная сессия базы данных

    Returns:
        ReviewService: Сервис для работы с отзывами
    """
    return container.review_service(db=db)


async def get_categories_service(
        db: AsyncSession = Depends(get_db)
) -> CategoryService:
    """
    Получает сервис категорий через DI-контейнер
    Args:
        db: Асинхронная сессия базы данных

    Returns:
        CategoryService: Сервис для работы с категориями товаров
    """
    return container.category_service(db=db)


def get_access_token(request: Request) -> str:
    """
    Извлекает access token из cookies запроса.

    Args:
        request: HTTP-запрос FastAPI

    Returns:
        str: Access token из cookies

    Raises:
        TokenAbsentException: Если токен отсутствует в cookies
    """
    token = request.cookies.get("access_token")
    if not token:
        raise TokenAbsentException
    return token


def get_refresh_token(request: Request) -> str:
    """
    Извлекает refresh token из cookies запроса.

    Args:
        request: HTTP-запрос FastAPI

    Returns:
        str: Refresh token из cookies

    Raises:
        TokenExpiredException: Если токен отсутствует в cookies
    """
    token = request.cookies.get("refresh_token")
    if not token:
        raise TokenExpiredException
    return token

async def get_current_user(
    token: str = Depends(get_access_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Получает текущего аутентифицированного пользователя из JWT токена.

    Декодирует access token, проверяет его валидность и срок действия,
    затем получает данные пользователя из базы данных.

    Args:
        token: Access token из cookies (получается через get_access_token)
        db: Асинхронная сессия базы данных

    Returns:
        UserItem: Доменная сущность текущего пользователя

    Raises:
        IncorrectTokenFormatException: Если токен имеет неверный формат
        TokenExpiredException: Если токен истёк
        UserIsNotPresentException: Если пользователь не найден в базе данных
    """
    try:  # декодим токен и достаём данные из payload
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except JWTError:
        raise IncorrectTokenFormatException
    expire: str = payload.get("exp")  # достали время истечения токена
    if (not expire) or int(expire) < datetime.now(tz=timezone.utc).timestamp():
        raise TokenExpiredException

    user_id: str = payload.get("sub")  # достали id
    if not user_id:
        raise UserIsNotPresentException

    user_repository = container.users_repository(db=db)
    user = await user_repository.get_user_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException
    return user


async def get_current_user_or_none(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserItem | None:
    """
    Получает текущего пользователя из JWT токена или возвращает None.

    Используется для эндпоинтов, где авторизация не обязательна.
    Если токен отсутствует, невалиден или истёк, возвращает None вместо исключения.

    Args:
        request: HTTP-запрос FastAPI
        db: Асинхронная сессия базы данных

    Returns:
        Доменная сущность пользователя или None, если пользователь не аутентифицирован
    """
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except JWTError:
        return None

    expire: str | None = payload.get("exp")
    if (not expire) or int(expire) < datetime.now(tz=timezone.utc).timestamp():
        return None

    user_id: str | None = payload.get("sub")
    if not user_id:
        return None

    user_repository = container.users_repository(db=db)
    user = await user_repository.get_user_by_id(int(user_id))
    return user