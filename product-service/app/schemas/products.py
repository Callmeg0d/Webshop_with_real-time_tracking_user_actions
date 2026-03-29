from enum import Enum
from typing import TypedDict

from pydantic import BaseModel, ConfigDict, Field


class ProductPayload(TypedDict):
    """Payload товара для Kafka (product_created / product_removed)"""
    product_id: int
    name: str
    description: str
    price: int
    product_quantity: int
    image: str
    features: dict[str, str]
    category_id: int


class SProductCreate(BaseModel):
    product_id: int | None = None
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=5)
    price: int = Field(..., ge=0)
    product_quantity: int = Field(..., ge=0)
    image: str = Field(..., min_length=1)
    features: dict[str, str] = Field(..., min_length=1)
    category_id: int = Field(..., ge=1)


class SProductUpdate(BaseModel):
    """Частичное обновление товара"""
    name: str | None = None
    description: str | None = None
    price: int | None = None
    product_quantity: int | None = None
    image: str | None = None
    features: dict[str, str] | None = None
    category_id: int | None = None


class SProducts(BaseModel):
    product_id: int
    name: str
    description: str
    price: int
    product_quantity: int
    image: str | None
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