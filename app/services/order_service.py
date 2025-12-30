from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.orders import OrderItem
from app.domain.interfaces.orders_repo import IOrdersRepository
from app.domain.interfaces.products_repo import IProductsRepository
from app.domain.interfaces.carts_repo import ICartsRepository
from app.domain.interfaces.users_repo import IUsersRepository
from app.services.order_notification_service import OrderNotificationService
from app.services.order_validator import OrderValidator
from app.services.payment_service import PaymentService
from app.schemas.carts import SCartItemForOrder
from app.schemas.orders import SUserOrder, SOrderItemWithImage


class OrderService:
    def __init__(self,
                 orders_repository: IOrdersRepository,
                 users_repository: IUsersRepository,
                 products_repository: IProductsRepository,
                 carts_repository: ICartsRepository,
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

        async with UnitOfWork(self.db):
            cart_items_raw = await self.carts_repository.get_cart_items(user_id)
            total_cost = await self.carts_repository.get_total_cost(user_id)
            
            # Преобразуем SCartItem в SCartItemForOrder для валидатора
            cart_items = [
                SCartItemForOrder(product_id=item.product_id, quantity=item.quantity)
                for item in cart_items_raw
            ]

            await self.validator.validate_order(user_id, cart_items, total_cost)

            order_data = await self._prepare_order_data(user_id, cart_items, total_cost)

            order = await self.orders_repository.create_order(order_data)

            await self._decrease_stock_items(cart_items)
            await self.payment.process_payment(user_id, total_cost)
            await self.carts_repository.clear_cart(user_id)

        # Отправляем уведомление
        await self.notification.send_order_confirmation(user_id, order)

        return order

    async def _decrease_stock_items(self, cart_items: list[SCartItemForOrder]) -> None:
        """
        Уменьшает остатки товаров на складе при создании заказа.

        Args:
            cart_items: Список товаров с полями product_id и quantity
        """
        for item in cart_items:
            await self.products_repository.decrease_stock(
                item.product_id,
                item.quantity
            )

    async def _prepare_order_data(self,
                                  user_id: int,
                                  cart_items: list[SCartItemForOrder],
                                  total_cost: int) -> OrderItem:
        delivery_address = await self.users_repository.get_delivery_address(user_id)
        order_items = [
            {"product_id": item.product_id, "quantity": item.quantity}
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

    async def get_user_orders(self, user_id: int) -> list[SUserOrder]:
        orders = await self.orders_repository.get_by_user_id(user_id)
        result = []
        
        for order in orders:
            if not order.order_items:
                continue

            order_items_with_images = []
            for item in order.order_items:
                product_id = item.get("product_id")
                product_image_url = None
                
                if product_id:
                    product = await self.products_repository.get_product_by_id(int(product_id))
                    if product:
                        product_image_url = (
                            f"/static/images/{product.image}.webp"
                            if product.image is not None
                            else None
                        )
                
                order_items_with_images.append(SOrderItemWithImage(
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    product_image_url=product_image_url
                ))

            result.append(SUserOrder(
                id=order.order_id,
                created_at=order.created_at,
                status=order.status,
                delivery_address=order.delivery_address,
                order_items=order_items_with_images,
                total_cost=order.total_cost
            ))

        return result
