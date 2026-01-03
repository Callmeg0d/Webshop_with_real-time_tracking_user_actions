from typing import Protocol

from pydantic import EmailStr

from app.domain.entities.users import UserItem


class IUsersRepository(Protocol):
    async def get_user_by_email(self, email: str | EmailStr) -> UserItem | None:
        ...

    async def get_user_by_id(self, user_id: int) -> UserItem | None:
        ...

    async def get_users_by_ids(self, user_ids: list[int]) -> dict[int, UserItem]:
        ...

    async def create_user(self, user: UserItem) -> UserItem:
        ...

    async def get_delivery_address(self, user_id: int) -> str | None:
        ...

    async def get_balance_with_lock(self, user_id: int) -> int | None:
        ...

    async def decrease_balance(self, user_id: int, cost: int) -> int | None:
        ...

    async def increase_balance(self, user_id: int, amount: int) -> None:
        ...

    async def change_delivery_address(self, user_id: int, new_address: str) -> str:
        ...

    async def change_user_name(self, user_id: int, new_name: str) -> str:
        ...

