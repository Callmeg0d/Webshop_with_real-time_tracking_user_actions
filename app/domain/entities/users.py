from dataclasses import dataclass
from typing import Optional

from pydantic import EmailStr


@dataclass
class UserItem:
    """Domain entity для пользователей."""
    email: EmailStr
    hashed_password: str
    delivery_address: Optional[str] = None
    name: Optional[str] = None
    id: int | None = None  # None при создании, int после сохранения в БД
    balance: int = 0