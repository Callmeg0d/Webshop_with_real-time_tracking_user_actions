from enum import Enum
from pydantic import BaseModel, ConfigDict


class SProducts(BaseModel):
    product_id: int
    name: str
    description: str
    price: int
    product_quantity: int
    image: int | None
    features: dict[str, str] | None
    category_id: int

    model_config = ConfigDict(from_attributes=True)

class SortEnum(str, Enum):
    ASC = "ASC"
    DESC = "DESC"

class Pagination(BaseModel):
    page: int
    per_page: int
    order: SortEnum


class SProductsCount(BaseModel):
    total: int