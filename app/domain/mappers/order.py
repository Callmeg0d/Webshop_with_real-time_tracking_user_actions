from app.domain.entities.orders import OrderItem
from app.models import Orders


class OrderMapper:
    @staticmethod
    def to_entity(orm_model: Orders) -> OrderItem:
        """Преобразует ORM модель в domain entity."""
        return OrderItem(
            order_id=orm_model.order_id,
            user_id=orm_model.user_id,
            created_at=orm_model.created_at,
            status=orm_model.status,
            delivery_address=orm_model.delivery_address,
            order_items=orm_model.order_items,
            total_cost=orm_model.total_cost
        )

    @staticmethod
    def to_orm(entity: OrderItem) -> dict:
        """Преобразует entity в данные для ORM."""
        data = {
            "user_id": entity.user_id,
            "created_at": entity.created_at,
            "status": entity.status,
            "delivery_address": entity.delivery_address,
            "order_items": entity.order_items,
            "total_cost": entity.total_cost,
        }
        return data
