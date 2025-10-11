from typing import Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Users
from app.repositories.base_repository import BaseRepository


class UsersRepository(BaseRepository[Users]):
    def __init__(self, db: AsyncSession):
        super().__init__(Users, db)

    async def create_user(self, user_data: dict) -> Users:
        """Создаёт нового пользователя"""
        user = Users(**user_data)
        self.db.add(user)
        return user

    async def get_delivery_address(self, user_id: int) -> Optional[str]:
        """Получает адрес доставки пользователя"""
        user = await self.get(user_id)
        return user.delivery_address if user else None

    async def change_delivery_address(self, user_id: int, new_address: str) -> Optional[str]:
        await self.db.execute(
            update(Users).
            where(Users.id == user_id).
            values(delivery_address=new_address)
        )
        return new_address

    async def change_user_name(self, user_id: int, new_name: str) -> Optional[str]:
        await self.db.execute(
            update(Users).where(Users.id == user_id).values(name=new_name)
        )
        return new_name
