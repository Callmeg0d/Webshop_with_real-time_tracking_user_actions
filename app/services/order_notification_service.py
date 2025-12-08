from app.domain.entities.orders import OrderItem
from app.domain.interfaces.users_repo import IUsersRepository
from app.messaging.publisher import publish_order_confirmation


class OrderNotificationService:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository


    async def send_order_confirmation(self, user_id: int, order: OrderItem):
        user = await self.users_repository.get_user_by_id(user_id)
        if user and user.email:
            order_dict = {
                "order_id": order.order_id,
                "created_at": order.created_at,
                "status": order.status,
                "delivery_address": order.delivery_address,
                "order_items": order.order_items,
                "total_cost": order.total_cost
            }
            await publish_order_confirmation(order_dict, user.email)