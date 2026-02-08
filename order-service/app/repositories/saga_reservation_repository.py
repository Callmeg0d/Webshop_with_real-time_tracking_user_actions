from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.saga_reservation import OrderSagaReservationItem
from app.domain.mappers.saga_reservation import SagaReservationMapper
from app.models.saga_reservation import OrderSagaReservation


class SagaReservationRepository:
    """Репозиторий для состояния резерваций саги по заказу."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.mapper = SagaReservationMapper()

    async def get_by_order_id(self, order_id: int) -> OrderSagaReservationItem | None:
        """Возвращает запись по order_id или None."""
        row = await self.db.get(OrderSagaReservation, order_id)
        return self.mapper.to_entity(row) if row else None

    async def set_stock_done(self, order_id: int) -> None:
        """Создаёт запись при отсутствии и выставляет stock_done=True."""
        row = await self.db.get(OrderSagaReservation, order_id)
        if row is None:
            row = OrderSagaReservation(order_id=order_id, stock_done=False, balance_done=False)
            self.db.add(row)
        row.stock_done = True

    async def set_balance_done(self, order_id: int) -> None:
        """Создаёт запись при отсутствии и выставляет balance_done=True."""
        row = await self.db.get(OrderSagaReservation, order_id)
        if row is None:
            row = OrderSagaReservation(order_id=order_id, stock_done=False, balance_done=False)
            self.db.add(row)
        row.balance_done = True

    async def delete_by_order_id(self, order_id: int) -> None:
        """Удаляет запись по order_id."""
        row = await self.db.get(OrderSagaReservation, order_id)
        if row is not None:
            await self.db.delete(row)
