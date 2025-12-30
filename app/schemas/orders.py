from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SOrderItem(BaseModel):
    """Схема для элемента заказа."""
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class SOrderItemWithImage(BaseModel):
    """Схема для элемента заказа с изображением товара."""
    product_id: int
    quantity: int
    product_image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SOrderResponse(BaseModel):
    order_id: int
    user_id: int
    created_at: datetime
    status: str
    delivery_address: str
    order_items: list[SOrderItem]
    total_cost: int

    model_config = ConfigDict(from_attributes=True)


class SUserOrder(BaseModel):
    """Схема для заказа пользователя с полной информацией."""
    id: int
    created_at: datetime
    status: str
    delivery_address: str
    order_items: list[SOrderItemWithImage]
    total_cost: int

    model_config = ConfigDict(from_attributes=True)
