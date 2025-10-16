from datetime import datetime
from typing import AsyncGenerator

from fastapi import Depends, Request
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_maker
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.services.auth_service import AuthService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.services.review_service import ReviewService
from app.services.user_service import UserService
from app.repositories import (
    OrdersRepository,
    ProductsRepository,
    CartsRepository,
    UsersRepository,
    ReviewRepository
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
        
async def get_orders_service(
    db: AsyncSession = Depends(get_db)
) -> OrderService:

    return OrderService(
        orders_repository=OrdersRepository(db),
        products_repository=ProductsRepository(db),
        carts_repository=CartsRepository(db),
        users_repository=UsersRepository(db),
        db=db
    )

async def get_products_service(
        db: AsyncSession = Depends(get_db)
) -> ProductService:
    return ProductService(
        product_repository=ProductsRepository(db),
        db=db
    )

async def get_carts_service(
        db: AsyncSession = Depends(get_db)
) -> CartService:
    return CartService(
        cart_repository=CartsRepository(db),
        db=db
    )

async def get_users_service(
        db: AsyncSession = Depends(get_db)
) -> UserService:
    return UserService(
        user_repository=UsersRepository(db),
        db=db
    )

async def get_auth_service(
        db: AsyncSession = Depends(get_db)
) -> AuthService:
    return AuthService(
        user_repository=UsersRepository(db),
        db=db
    )

async def get_reviews_service(
        db: AsyncSession = Depends(get_db)
) -> ReviewService:
    return ReviewService(
        review_repository=ReviewRepository(db),
        db=db
    )


def get_access_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise TokenAbsentException
    return token


def get_refresh_token(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise TokenExpiredException
    return token


async def get_current_user(
    token: str = Depends(get_access_token),
    db: AsyncSession = Depends(get_db)
):
    try:  # декодим токен и достаём данные из payload
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except JWTError:
        raise IncorrectTokenFormatException
    expire: str = payload.get("exp")  # достали время истечения токена
    if (not expire) or int(expire) < datetime.utcnow().timestamp():
        raise TokenExpiredException

    user_id: str = payload.get("sub")  # достали id
    if not user_id:
        raise UserIsNotPresentException

    user_repository = UsersRepository(db)
    user = await user_repository.get(int(user_id))
    if not user:
        raise UserIsNotPresentException
    return user