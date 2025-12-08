
from app.domain.interfaces.users_repo import IUsersRepository


class PaymentService:
    def __init__(self, users_repository: IUsersRepository):
        self.users_repository = users_repository


    async def process_payment(self, user_id:int, total_cost:int) :
        await self.users_repository.decrease_balance(user_id, total_cost)

