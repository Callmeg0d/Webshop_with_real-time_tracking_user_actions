from dataclasses import dataclass


@dataclass
class UserItem:
    """Domain entity для пользователей."""
    email: str
    hashed_password: str
    delivery_address: str | None = None
    name: str | None = None
    id: int | None = None  # None при создании, int после сохранения в БД
    balance: int = 0

