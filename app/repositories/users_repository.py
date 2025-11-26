from typing import Optional

from pydantic import EmailStr
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.users import UserItem
from app.domain.mappers.user import UserMapper
from app.models import Users


class UsersRepository:
    """
    Репозиторий для работы с юзерами.

    Работает с domain entities (UserItem), используя маппер для преобразования
    между entities и ORM моделями.
    """

    def __init__(self, db: AsyncSession):
        """
        Инициализация репозитория пользователей.

        Args:
            db: Асинхронная сессия базы данных
        """
        self.db = db
        self.mapper = UserMapper()

    async def get_user_by_email(self, email: str | EmailStr) -> Optional[UserItem]:
        """
        Находит пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            Доменная сущность пользователя либо `None`.
        """
        result = await self.db.execute(
            select(Users).where(Users.email == email)
        )
        orm_data = result.scalar_one_or_none()

        return self.mapper.to_entity(orm_data) if orm_data else None

    async def get_user_by_id(self, user_id: int) -> Optional[UserItem]:
        """
        Находит пользователя по идентификатору.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Доменная сущность пользователя либо `None`.
        """
        result = await self.db.execute(
            select(Users).where(Users.id == user_id)
        )
        orm_data = result.scalar_one_or_none()

        return self.mapper.to_entity(orm_data) if orm_data else None

    async def create_user(self, user: UserItem) -> UserItem:
        """
        Создаёт нового пользователя.

        Args:
            user: Доменная сущность пользователя, собранная сервисом.

        Returns:
            Доменная сущность с присвоенным `id`.
        """
        orm_data = self.mapper.to_orm(user)
        orm_model = Users(**orm_data)
        self.db.add(orm_model)
        await self.db.flush()

        return self.mapper.to_entity(orm_model)

    async def get_delivery_address(self, user_id: int) -> Optional[str]:
        """
        Получает адрес доставки пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Адрес доставки либо `None`, если пользователь не найден.
        """
        result = await self.db.execute(
            select(Users.delivery_address).where(Users.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_balance_with_lock(self, user_id: int) -> Optional[int]:
        """
        Получает текущий баланс пользователя с блокировкой строки (SELECT FOR UPDATE).

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Баланс пользователя или None, если пользователь не найден
        """
        result = await self.db.execute(
            select(Users.balance)
            .where(Users.id == user_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def decrease_balance(self, user_id: int, cost: int) -> Optional[int]:
        """
        Списывает указанную сумму с баланса пользователя.

        Args:
            user_id: Идентификатор пользователя.
            cost: Сумма списания (стоимость заказа), должна быть > 0

        Returns:
            Новый баланс пользователя после списания или None, если пользователь не найден

        """
        if cost <= 0:
            raise ValueError("Сумма списания должна быть больше нуля")
        
        await self.db.execute(
            update(Users)
            .where(Users.id == user_id)
            .values(balance=Users.balance - cost)
        )
        # Получаем актуальный баланс из БД
        result = await self.db.execute(
            select(Users.balance).where(Users.id == user_id)
        )
        return result.scalar_one_or_none()

    async def change_delivery_address(self, user_id: int, new_address: str) -> str:
        """
        Изменяет адрес доставки пользователя.

        Args:
            user_id: Идентификатор пользователя.
            new_address: Новый адрес доставки.

        Returns:
            Новый адрес доставки.
        """
        await self.db.execute(
            update(Users).
            where(Users.id == user_id).
            values(delivery_address=new_address)
        )
        return new_address

    async def change_user_name(self, user_id: int, new_name: str) -> str:
        """
        Изменяет имя пользователя.

        Args:
            user_id: Идентификатор пользователя.
            new_name: Новое имя пользователя.

        Returns:
            Новое имя пользователя.
        """
        await self.db.execute(
            update(Users).where(Users.id == user_id).values(name=new_name)
        )
        return new_name
