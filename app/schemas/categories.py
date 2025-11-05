from typing import Optional
from pydantic import BaseModel, ConfigDict


class SCategoryResponse(BaseModel):
    """Схема для ответа с категорией."""
    id: int
    name: str
    description: Optional[str]  # Опциональное поле, как в entity

    model_config = ConfigDict(from_attributes=True)


class SCategoryCreate(BaseModel):
    """Схема для создания категории."""
    name: str
    description: Optional[str] = None
