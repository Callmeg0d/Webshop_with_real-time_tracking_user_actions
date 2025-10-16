from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Users
from app.repositories.base_repository import BaseRepository


class UsersRepository(BaseRepository[Users]):
    """
    Репозиторий для работы с пользователями.

    Предоставляет методы для управления пользователями, включая создание,
    поиск и обновление данных пользователей.
    """

    def __init__(self, db: AsyncSession):
        """
        Инициализация репозитория пользователей.

        Args:
            db: Асинхронная сессия базы данных
        """
        super().__init__(Users, db)

    async def get_user_by_email(self, email: str) -> Optional[Users]:
        """
        Находит пользователя по email.

        Args:
            email: Email пользователя

        Returns:
            Объект пользователя если найден, иначе None
        """
        result = await self.db.execute(
            select(Users).where(Users.email == email)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: dict) -> Users:
        """
        Создаёт нового пользователя.

        Args:
            user_data: Словарь с данными пользователя

        Returns:
            Созданный объект пользователя
        """
        user = Users(**user_data)
        self.db.add(user)
        return user

    async def get_delivery_address(self, user_id: int) -> Optional[str]:
        """
        Получает адрес доставки пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Адрес доставки если найден, иначе None
        """
        user = await self.get(user_id)
        return user.delivery_address if user else None

    async def change_delivery_address(self, user_id: int, new_address: str) -> Optional[str]:
        """
        Изменяет адрес доставки пользователя.

        Args:
            user_id: ID пользователя
            new_address: Новый адрес доставки

        Returns:
            Новый адрес доставки
        """
        await self.db.execute(
            update(Users).
            where(Users.id == user_id).
            values(delivery_address=new_address)
        )
        return new_address

    async def change_user_name(self, user_id: int, new_name: str) -> Optional[str]:
        """
        Изменяет имя пользователя.

        Args:
            user_id: ID пользователя
            new_name: Новое имя пользователя

        Returns:
            Новое имя пользователя
        """
        await self.db.execute(
            update(Users).where(Users.id == user_id).values(name=new_name)
        )
        return new_name
