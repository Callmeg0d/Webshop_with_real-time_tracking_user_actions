from shared import get_logger

from app.domain.entities.users import UserItem
from app.domain.interfaces.users_repo import IUsersRepository
from app.domain.interfaces.unit_of_work import IUnitOfWorkFactory

logger = get_logger(__name__)


class UserService:
    def __init__(
            self,
            user_repository: IUsersRepository,
            uow_factory: IUnitOfWorkFactory
    ):
        self.user_repository = user_repository
        self.uow_factory = uow_factory

    async def create_user(self, user_data: UserItem) -> UserItem:
        logger.info(f"Creating user with email: {user_data.email}")
        try:
            async with self.uow_factory.create():
                user = await self.user_repository.create_user(user_data)
            logger.info(f"User created successfully, user_id: {user.id}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}", exc_info=True)
            raise

    async def get_delivery_address(self, user_id: int) -> str | None:
        logger.debug(f"Fetching delivery address for user {user_id}")
        try:
            address = await self.user_repository.get_delivery_address(user_id=user_id)
            logger.debug(f"Delivery address retrieved for user {user_id}")
            return address
        except Exception as e:
            logger.error(f"Error fetching delivery address for user {user_id}: {e}", exc_info=True)
            raise

    async def change_delivery_address(self, user_id: int, new_address: str) -> None:
        logger.info(f"Changing delivery address for user {user_id}")
        try:
            async with self.uow_factory.create():
                await self.user_repository.change_delivery_address(
                    user_id=user_id,
                    new_address=new_address
                )
            logger.info(f"Delivery address updated successfully for user {user_id}")
        except Exception as e:
            logger.error(f"Error changing delivery address for user {user_id}: {e}", exc_info=True)
            raise

    async def change_user_name(self, user_id: int, new_name: str) -> None:
        logger.info(f"Changing name for user {user_id}")
        try:
            async with self.uow_factory.create():
                await self.user_repository.change_user_name(user_id, new_name)
            logger.info(f"Name updated successfully for user {user_id}")
        except Exception as e:
            logger.error(f"Error changing name for user {user_id}: {e}", exc_info=True)
            raise

    async def get_balance(self, user_id: int) -> int | None:
        """Получает баланс пользователя"""
        logger.debug(f"Fetching balance for user {user_id}")
        try:
            balance = await self.user_repository.get_balance_with_lock(user_id)
            logger.debug(f"Balance retrieved for user {user_id}: {balance}")
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance for user {user_id}: {e}", exc_info=True)
            raise

    async def decrease_balance(self, user_id: int, amount: int) -> None:
        """Уменьшает баланс пользователя"""
        logger.info(f"Decreasing balance for user {user_id} by {amount}")
        try:
            async with self.uow_factory.create():
                await self.user_repository.decrease_balance(user_id, amount)
            logger.info(f"Balance decreased successfully for user {user_id}")
        except Exception as e:
            logger.error(f"Error decreasing balance for user {user_id}: {e}", exc_info=True)
            raise

    async def increase_balance(self, user_id: int, amount: int) -> None:
        """Увеличивает баланс пользователя (компенсация)"""
        logger.info(f"Increasing balance for user {user_id} by {amount} (compensation)")
        try:
            async with self.uow_factory.create():
                await self.user_repository.increase_balance(user_id, amount)
            logger.info(f"Balance increased successfully for user {user_id}")
        except Exception as e:
            logger.error(f"Error increasing balance for user {user_id}: {e}", exc_info=True)
            raise

    async def get_users_by_ids(self, user_ids: list[int]) -> dict[int, UserItem]:
        """
        Получает пользователей по списку идентификаторов.

        Args:
            user_ids: Список идентификаторов пользователей

        Returns:
            Словарь {user_id: UserItem} с найденными пользователями
        """
        logger.debug(f"Fetching users batch for {len(user_ids)} user IDs")
        try:
            users = await self.user_repository.get_users_by_ids(user_ids)
            logger.debug(f"Retrieved {len(users)} users from batch request")
            return users
        except Exception as e:
            logger.error(f"Error fetching users batch: {e}", exc_info=True)
            raise

