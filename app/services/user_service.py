from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Users
from app.repositories import UsersRepository


class UserService:
    def __init__(
            self,
            user_repository: UsersRepository,
            db: AsyncSession
    ):
        self.user_repository = user_repository
        self.db = db

    async def create_user(self, user_data: dict) -> Users:
        user = await self.user_repository.create_user(user_data)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_delivery_address(self, user_id: int) -> Optional[str]:
        address = await self.user_repository.get_delivery_address(user_id=user_id)
        return address

    async def change_delivery_address(self, user_id: int, new_address: str) -> None:
        await self.user_repository.change_delivery_address(
            user_id=user_id,
            new_address=new_address
        )
        await self.db.commit()

    async def change_user_name(self, user_id: int, new_name: str) -> None:
        await self.user_repository.change_user_name(user_id, new_name)
        await self.db.commit()

