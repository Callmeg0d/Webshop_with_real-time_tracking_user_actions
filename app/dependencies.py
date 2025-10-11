from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import async_session_maker
from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.repositories import (
    OrdersRepository,
    ProductsRepository,
    CartsRepository,
    UsersRepository
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