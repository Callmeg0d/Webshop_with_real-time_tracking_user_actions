from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.orders import OrderItem
from app.repositories import (
    OrdersRepository,
    ProductsRepository,
    CartsRepository,
    UsersRepository
)
from app.services.order_notification_service import OrderNotificationService
from app.services.order_validator import OrderValidator
from app.services.payment_service import PaymentService


class OrderService:
    def __init__(self,
                 orders_repository: OrdersRepository,
                 users_repository: UsersRepository,
                 products_repository: ProductsRepository,
                 carts_repository: CartsRepository,
                 order_validator: OrderValidator,
                 payment_service: PaymentService,
                 notification_service: OrderNotificationService,
                 db: AsyncSession
                 ):
        self.orders_repository = orders_repository
        self.users_repository = users_repository
        self.products_repository = products_repository
        self.carts_repository = carts_repository
        self.validator = order_validator
        self.payment = payment_service
        self.notification = notification_service
        self.db = db


    async def create_order(self, user_id: int) -> OrderItem:

        cart_items = await self.carts_repository.get_cart_items(user_id)
        total_cost = await self.carts_repository.get_total_cost(user_id)

        await self.validator.validate_order(user_id, cart_items, total_cost)

        order_data =  await self._prepare_order_data(user_id, cart_items, total_cost)

        order = await self.orders_repository.create_order(order_data)

        await self._decrease_stock_items(cart_items)
        await self.payment.process_payment(user_id, total_cost)
        await self.carts_repository.clear_cart(user_id)

        await self.db.commit()

        # Отправляем уведомление
        await self.notification.send_order_confirmation(user_id, order)

        return order

    async def _decrease_stock_items(self, cart_items: List[dict]) -> None:
        """
        Уменьшает остатки товаров на складе при создании заказа.

        Args:
            cart_items: Список товаров с полями product_id и quantity
        """
        for item in cart_items:
            await self.products_repository.decrease_stock(
                item["product_id"],
                item["quantity"]
            )

    async def _prepare_order_data(self,
                                  user_id: int,
                                  cart_items: List[dict],
                                  total_cost: int) -> OrderItem:
        delivery_address = await self.users_repository.get_delivery_address(user_id)
        order_items = [
            {"product_id": item["product_id"], "quantity": item["quantity"]}
            for item in cart_items
        ]

        return OrderItem(
            user_id=user_id,
            created_at=datetime.now().replace(microsecond=0),
            status="Arriving",
            delivery_address=delivery_address,
            order_items=order_items,
            total_cost=total_cost
        )

    async def get_user_orders(self, user_id: int) -> List[dict]:
        orders = await self.orders_repository.get_by_user_id(user_id)
        for order in orders:
            if not order.order_items:
                continue

            for item in order.order_items:
                product_id = item.get("product_id")
                if product_id:
                    product = await self.products_repository.get_product_by_id(int(product_id))
                    if product:
                        item["product_image_url"] = (
                            f"/static/images/{product.image}.webp"
                            if product.image is not None
                            else None
                        )

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
