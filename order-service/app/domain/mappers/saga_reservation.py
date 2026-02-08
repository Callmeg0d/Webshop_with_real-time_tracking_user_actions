from app.domain.entities.saga_reservation import OrderSagaReservationItem
from app.models.saga_reservation import OrderSagaReservation


class SagaReservationMapper:
    @staticmethod
    def to_entity(orm_model: OrderSagaReservation) -> OrderSagaReservationItem:
        """Преобразует ORM модель в domain entity."""
        return OrderSagaReservationItem(
            order_id=orm_model.order_id,
            stock_done=orm_model.stock_done,
            balance_done=orm_model.balance_done,
            updated_at=orm_model.updated_at,
        )

    @staticmethod
    def to_orm(entity: OrderSagaReservationItem) -> dict:
        """Преобразует entity в данные для ORM."""
        return {
            "order_id": entity.order_id,
            "stock_done": entity.stock_done,
            "balance_done": entity.balance_done,
        }
