from shared import ReserveBalanceResult, SagaIdempotencyKey, get_logger

from app.repositories.idempotency_key_repository import IdempotencyKeyRepository
from app.repositories.users_repository import UsersRepository

logger = get_logger(__name__)


class BalanceReservationService:
    """Сервис резервации баланса и компенсаций в рамках саги."""

    def __init__(
        self,
        idempotency_key_repository: IdempotencyKeyRepository,
        users_repository: UsersRepository,
    ):
        self.idempotency_key_repository = idempotency_key_repository
        self.users_repository = users_repository

    async def reserve_balance(self, order_id: int, user_id: int, total_cost: int) -> ReserveBalanceResult:
        """
        Резервирует баланс для заказа.
        """
        if await self.idempotency_key_repository.exists(
            SagaIdempotencyKey.ORDER_PROCESSING, str(order_id)
        ):
            return ReserveBalanceResult.ALREADY_DONE

        balance = await self.users_repository.get_balance_with_lock(user_id)
        if balance is None:
            return ReserveBalanceResult.USER_NOT_FOUND
        if balance < total_cost:
            return ReserveBalanceResult.INSUFFICIENT_BALANCE

        await self.users_repository.decrease_balance(user_id, total_cost)
        await self.idempotency_key_repository.add(
            SagaIdempotencyKey.ORDER_PROCESSING, str(order_id)
        )
        return ReserveBalanceResult.SUCCESS

    async def record_balance_compensation(
        self, order_id: int, user_id: int, amount: int
    ) -> bool:
        """
        Фиксирует возврат баланса (компенсация).

        Returns: True если операция выполнена, False если уже была выполнена.

        """
        if await self.idempotency_key_repository.exists(
            SagaIdempotencyKey.COMPENSATION_BALANCE, str(order_id)
        ):
            return False
        await self.idempotency_key_repository.add(
            SagaIdempotencyKey.COMPENSATION_BALANCE, str(order_id)
        )
        await self.users_repository.increase_balance(user_id, amount)
        return True
