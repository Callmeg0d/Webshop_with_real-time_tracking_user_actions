from app.services.user_client import decrease_user_balance


class PaymentService:
    def __init__(self):
        pass

    async def process_payment(self, user_id: int, total_cost: int) -> None:
        """
        Обрабатывает оплату заказа - списывает средства с баланса пользователя.

        Args:
            user_id: ID пользователя
            total_cost: Сумма для списания
        """
        await decrease_user_balance(user_id, total_cost)

