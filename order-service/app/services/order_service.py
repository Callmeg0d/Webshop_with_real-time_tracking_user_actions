from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.orders import OrderItem
from app.domain.interfaces.orders_repo import IOrdersRepository
from app.schemas.orders import SCartItemForOrder, SUserOrder, SOrderItemWithImage
from app.services.cart_client import get_cart_items, get_cart_total
from app.services.product_client import get_product
from app.services.order_validator import OrderValidator
from app.services.payment_service import PaymentService
from app.services.order_notification_service import OrderNotificationService
from app.services.user_client import get_user_delivery_address
from app.messaging.publisher import (
    publish_order_processing_started,
    publish_order_confirmed,
    publish_stock_increase,
    publish_balance_increase
)
from app.constants import ORDER_STATUS_PENDING, ORDER_STATUS_CONFIRMED, ORDER_STATUS_FAILED

class OrderService:
    def __init__(
        self,
        orders_repository: IOrdersRepository,
        order_validator: OrderValidator,
        payment_service: PaymentService,
        notification_service: OrderNotificationService,
        db: AsyncSession
    ):
        self.orders_repository = orders_repository
        self.validator = order_validator
        self.payment = payment_service
        self.notification = notification_service
        self.db = db

    async def create_order(self, user_id: int) -> OrderItem:
        async with UnitOfWork(self.db):
            # Получаем корзину из cart-service
            cart_items_raw = await get_cart_items(user_id)
            total_cost = await get_cart_total(user_id)
            
            # Преобразуем в SCartItemForOrder для валидатора
            cart_items = [
                SCartItemForOrder(product_id=item["product_id"], quantity=item["quantity"])
                for item in cart_items_raw
            ]

            await self.validator.validate_order(user_id, cart_items, total_cost)

            # Создаем заказ со статусом Pending
            order_data = await self._prepare_order_data(user_id, cart_items, total_cost)
            order = await self.orders_repository.create_order(order_data)

        # Публикуем событие начала обработки заказа (Saga)
        await publish_order_processing_started({
            "order_id": order.order_id,
            "user_id": user_id,
            "order_items": order.order_items,
            "total_cost": order.total_cost
        })

        return order

    async def confirm_order(self, order_id: int) -> None:
        """
        Подтверждает заказ после успешной резервации всех ресурсов.
        
        Args:
            order_id: ID заказа
        """
        # Идемпотентность: проверяем статус перед подтверждением
        order = await self.orders_repository.get_order_by_id(order_id)
        if not order or order.status != ORDER_STATUS_PENDING:
            return
        
        async with UnitOfWork(self.db):
            await self.orders_repository.update_order_status(order_id, ORDER_STATUS_CONFIRMED)
        
        # Получаем заказ для публикации события
        order = await self.orders_repository.get_order_by_id(order_id)
        if order:
            order_dict = {
                "order_id": order.order_id,
                "user_id": order.user_id,
                "created_at": order.created_at.isoformat() if hasattr(order.created_at, 'isoformat') else str(order.created_at),
                "status": order.status,
                "delivery_address": order.delivery_address,
                "order_items": order.order_items,
                "total_cost": order.total_cost
            }
            await publish_order_confirmed(order_dict)
            
            # Отправляем уведомление
            await self.notification.send_order_confirmation(order.user_id, order)

    async def fail_order(self, order_id: int, reason: str) -> None:
        """
        Отменяет заказ и запускает компенсацию.
        
        Args:
            order_id: ID заказа
            reason: Причина отмены
        """
        # Идемпотентность: проверяем статус перед отменой
        order = await self.orders_repository.get_order_by_id(order_id)
        if not order or order.status != ORDER_STATUS_PENDING:
            return
        
        async with UnitOfWork(self.db):
            await self.orders_repository.update_order_status(order_id, ORDER_STATUS_FAILED)
        
        # Компенсирующие действия - возврат ресурсов
        if order:
            for item in order.order_items:
                await publish_stock_increase(order_id, item["product_id"], item["quantity"])
            
            await publish_balance_increase(order_id, order.user_id, order.total_cost)

    async def _prepare_order_data(
        self,
        user_id: int,
        cart_items: list[SCartItemForOrder],
        total_cost: int
    ) -> OrderItem:

        delivery_address = await get_user_delivery_address(user_id)
        order_items = [
            {"product_id": item.product_id, "quantity": item.quantity}
            for item in cart_items
        ]

        return OrderItem(
            user_id=user_id,
            created_at=datetime.now().date(),
            status=ORDER_STATUS_PENDING,
            delivery_address=delivery_address or "",
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
                    try:
                        product = await get_product(int(product_id))
                        if product and product.get("image") is not None:
                            product_image_url = f"/static/images/{product['image']}.webp"
                    except Exception:
                        pass
                
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

