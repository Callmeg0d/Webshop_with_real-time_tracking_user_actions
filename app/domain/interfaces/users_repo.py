from typing import Protocol, Optional

from pydantic import EmailStr

from app.domain.entities.users import UserItem


class IUsersRepository(Protocol):
    async def get_user_by_email(self, email: str | EmailStr) -> Optional[UserItem]:
        ...

    async def get_user_by_id(self, user_id: int) -> Optional[UserItem]:
        ...

    async def create_user(self, user: UserItem) -> UserItem:
        ...

    async def get_delivery_address(self, user_id: int) -> Optional[str]:
        ...

    async def get_balance_with_lock(self, user_id: int) -> Optional[int]:
        ...

    async def decrease_balance(self, user_id: int, cost: int) -> Optional[int]:
        ...

    async def change_delivery_address(self, user_id: int, new_address: str) -> str:
        ...

    async def change_user_name(self, user_id: int, new_name: str) -> str:
        ...

