from app.domain.entities.orders import OrderItem
from app.messaging.publisher import publish_order_confirmation
from app.services.user_client import get_user_email


class OrderNotificationService:
    def __init__(self):
        pass

    async def send_order_confirmation(self, user_id: int, order: OrderItem) -> None:
        """
        Отправляет уведомление о создании заказа через Kafka.

        Args:
            user_id: ID пользователя
            order: Доменная сущность заказа
        """
        user_email = await get_user_email(user_id)
        if user_email:
            order_dict = {
                "order_id": order.order_id,
                "created_at": order.created_at.isoformat() if hasattr(order.created_at, 'isoformat') else str(order.created_at),
                "status": order.status,
                "delivery_address": order.delivery_address,
                "order_items": order.order_items,
                "total_cost": order.total_cost
            }
            await publish_order_confirmation(order_dict, user_email)

