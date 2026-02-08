from shared import ReserveStockResult, SagaIdempotencyKey, get_logger

from app.repositories.idempotency_key_repository import IdempotencyKeyRepository
from app.repositories.products_repository import ProductsRepository

logger = get_logger(__name__)


class StockReservationService:
    """Сервис резервации остатков и компенсаций в рамках саги."""

    def __init__(
        self,
        idempotency_key_repository: IdempotencyKeyRepository,
        products_repository: ProductsRepository,
    ):
        self.idempotency_key_repository = idempotency_key_repository
        self.products_repository = products_repository

    async def reserve_stock(
        self, order_id: int, order_items: list[dict]
    ) -> tuple[ReserveStockResult, str | None]:
        """
        Резервирует остатки по позициям заказа.

        Returns: (result, error_message). error_message заполнен при INSUFFICIENT_STOCK.
        """
        if await self.idempotency_key_repository.exists(
            SagaIdempotencyKey.ORDER_PROCESSING, str(order_id)
        ):
            return ReserveStockResult.ALREADY_DONE, None

        reserved_any = False
        for item in order_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")
            if not product_id or not quantity:
                continue
            stock = await self.products_repository.get_stock_by_ids([product_id])
            available = stock.get(product_id, 0)
            if available < quantity:
                return (
                    ReserveStockResult.INSUFFICIENT_STOCK,
                    f"Insufficient stock for product {product_id}",
                )
            await self.products_repository.decrease_stock(product_id, quantity)
            reserved_any = True

        if not reserved_any:
            return (
                ReserveStockResult.INSUFFICIENT_STOCK,
                "No valid order items to reserve",
            )
        await self.idempotency_key_repository.add(
            SagaIdempotencyKey.ORDER_PROCESSING, str(order_id)
        )
        return ReserveStockResult.SUCCESS, None

    async def record_stock_compensation(
        self, order_id: int, product_id: int, quantity: int
    ) -> bool:
        """
        Фиксирует возврат остатков (компенсация).

        Returns: True если операция выполнена, False если уже была выполнена.
        """
        business_key = f"{order_id}:{product_id}"
        if await self.idempotency_key_repository.exists(
            SagaIdempotencyKey.COMPENSATION_STOCK, business_key
        ):
            return False
        await self.idempotency_key_repository.add(
            SagaIdempotencyKey.COMPENSATION_STOCK, business_key
        )
        await self.products_repository.increase_stock(product_id, quantity)
        return True
