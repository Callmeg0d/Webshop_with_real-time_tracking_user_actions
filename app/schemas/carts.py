from pydantic import BaseModel, ConfigDict


class UpdateCartItemRequest(BaseModel):
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class SCartItem(BaseModel):
    """Схема для товара в корзине."""
    product_id: int
    quantity: int
    total_cost: int

    model_config = ConfigDict(from_attributes=True)


class SCartItemWithProduct(BaseModel):
    """Схема для товара в корзине с полной информацией о продукте."""
    product_id: int
    name: str
    description: str
    price: int
    quantity: int
    total_cost: int
    product_quantity: int

    model_config = ConfigDict(from_attributes=True)


class SCartItemForOrder(BaseModel):
    """Схема для товара корзины при создании заказа."""
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)