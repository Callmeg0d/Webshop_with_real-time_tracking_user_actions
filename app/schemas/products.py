from typing import Optional

from pydantic import BaseModel, ConfigDict


class SProducts(BaseModel):
    product_id: int
    name: str
    description: str
    price: int
    product_quantity: int
    image: Optional[int]
    features: Optional[dict[str, str]]
    category_name: str

    model_config = ConfigDict(from_attributes=True)

