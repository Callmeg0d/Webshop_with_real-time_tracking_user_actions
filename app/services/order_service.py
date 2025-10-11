from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import (
    OrdersRepository,
    ProductsRepository,
    CartsRepository,
    UsersRepository
)
from app.exceptions import (
    NotEnoughProductsInStock,
    CannotMakeOrderWithoutItems,
    CannotMakeOrderWithoutAddress
)
from app.models import Orders
from app.websockets import send_product_update

class OrderService:
    def __init__(self,
                 orders_repository: OrdersRepository,
                 users_repository: UsersRepository,
                 products_repository: ProductsRepository,
                 carts_repository: CartsRepository,
                 db: AsyncSession
                 ):
        self.orders_repository = orders_repository
        self.users_repository = users_repository
        self.products_repository = products_repository
        self.carts_repository = carts_repository
        self.db = db


    async def create_order(self, user_id: int) -> Orders:
        # Проверяем наличие адреса
        delivery_address = await self.users_repository.get_delivery_address(user_id)
        if not delivery_address:
            raise CannotMakeOrderWithoutAddress

        # Получаем товары из корзины
        cart_items = await self.carts_repository.get_cart_items(user_id)
        if not cart_items:
            raise CannotMakeOrderWithoutItems

        # Проверяем остатки на складе
        product_ids = [item["product_id"] for item in cart_items]
        stock_items = await self.products_repository.get_stock_by_ids(product_ids)

        for item in cart_items:
            available = stock_items.get(item["product_id"], 0)
            if item["quantity"] > available:
                raise NotEnoughProductsInStock

        # Считаем общую стоимость
        total_cost = await self.carts_repository.get_total_cost(user_id)

        # Формируем данные заказа
        order_items = [
            {"product_id": item["product_id"], "quantity": item["quantity"]}
            for item in cart_items
        ]

        order_data = {
            "user_id": user_id,
            "created_at": datetime.now().replace(microsecond=0),
            "status": "Arriving",
            "delivery_address": delivery_address,
            "order_items": order_items,
            "total_cost": total_cost
        }
        # Создаём заказ
        order = await self.orders_repository.create_order(order_data)

        # Обновляем остатки
        for item in cart_items:
            await self.products_repository.decrease_stock(
                item["product_id"],
                item["quantity"]
            )
        # Очищаем корзину
        await self.carts_repository.clear_cart(user_id)

        await self.db.commit()
        await self.db.refresh(order)

        for item in cart_items:
            new_quantity = await self.products_repository.get_quantity(item["product_id"])
            if new_quantity is not None:
                await send_product_update(item["product_id"], new_quantity)

        return order

    async def get_user_orders(self, user_id: int) -> List[dict]:
        orders = await self.orders_repository.get_by_user_id(user_id)
        for order in orders:
            if not order.order_items:
                continue

            for item in order.order_items:
                product_id = item.get("product_id")
                if product_id:
                    product = await self.products_repository.get_product_by_id(product_id)
                    if product:
                        item["product_image_url"] = f"/static/images/{product.image}.webp"

        return [
            {
                "id": order.order_id,
                "created_at": order.created_at,
                "status": order.status,
                "delivery_address": order.delivery_address,
                "order_items": order.order_items,
                "total_cost": order.total_cost
            }
            for order in orders
        ]
