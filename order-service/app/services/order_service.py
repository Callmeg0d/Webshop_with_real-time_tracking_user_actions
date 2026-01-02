from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.orders import OrderItem
from app.domain.interfaces.orders_repo import IOrdersRepository
from app.schemas.orders import SCartItemForOrder, SUserOrder, SOrderItemWithImage
from app.services.cart_client import get_cart_items, get_cart_total, clear_cart
from app.services.product_client import get_product, decrease_stock
from app.services.order_validator import OrderValidator
from app.services.payment_service import PaymentService
from app.services.order_notification_service import OrderNotificationService
from app.services.user_client import get_user_delivery_address

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

            order_data = await self._prepare_order_data(user_id, cart_items, total_cost)

            order = await self.orders_repository.create_order(order_data)

            # Уменьшаем остатки в product-service
            for item in cart_items:
                await decrease_stock(item.product_id, item.quantity)
            
            await self.payment.process_payment(user_id, total_cost)
            await clear_cart(user_id)

        # Отправляем уведомление
        await self.notification.send_order_confirmation(user_id, order)

        return order

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
            status="Arriving",
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

