from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.users import UserItem
from app.domain.interfaces.users_repo import IUsersRepository


class UserService:
    def __init__(
            self,
            user_repository: IUsersRepository,
            db: AsyncSession
    ):
        self.user_repository = user_repository
        self.db = db

    async def create_user(self, user_data: UserItem) -> UserItem:
        async with UnitOfWork(self.db):
            user = await self.user_repository.create_user(user_data)
        return user

    async def get_delivery_address(self, user_id: int) -> str | None:
        address = await self.user_repository.get_delivery_address(user_id=user_id)
        return address

    async def change_delivery_address(self, user_id: int, new_address: str) -> None:
        async with UnitOfWork(self.db):
            await self.user_repository.change_delivery_address(
                user_id=user_id,
                new_address=new_address
            )

    async def change_user_name(self, user_id: int, new_name: str) -> None:
        async with UnitOfWork(self.db):
            await self.user_repository.change_user_name(user_id, new_name)

    async def get_balance(self, user_id: int) -> int | None:
        """Получает баланс пользователя"""
        return await self.user_repository.get_balance_with_lock(user_id)

    async def decrease_balance(self, user_id: int, amount: int) -> None:
        """Уменьшает баланс пользователя"""
        async with UnitOfWork(self.db):
            await self.user_repository.decrease_balance(user_id, amount)

    async def increase_balance(self, user_id: int, amount: int) -> None:
        """Увеличивает баланс пользователя (компенсация)"""
        async with UnitOfWork(self.db):
            await self.user_repository.increase_balance(user_id, amount)

    async def get_users_by_ids(self, user_ids: list[int]) -> dict[int, UserItem]:
        """
        Получает пользователей по списку идентификаторов.

        Args:
            user_ids: Список идентификаторов пользователей

        Returns:
            Словарь {user_id: UserItem} с найденными пользователями
        """
        return await self.user_repository.get_users_by_ids(user_ids)

