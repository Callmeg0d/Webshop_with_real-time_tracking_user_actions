from typing import Optional

from pydantic import BaseModel, ConfigDict


class SReviewCreate(BaseModel):
    rating: int
    feedback: str

    model_config = ConfigDict(from_attributes=True)


class SReviewWithUser(BaseModel):
    """DTO для отзыва с данными пользователя."""
    user_email: str
    user_name: Optional[str]
    rating: int
    feedback: str

    model_config = ConfigDict(from_attributes=True)

