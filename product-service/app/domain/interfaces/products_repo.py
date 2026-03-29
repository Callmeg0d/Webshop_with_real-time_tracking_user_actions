from typing import Protocol

from app.domain.entities.product import ProductItem
from app.schemas.products import Pagination, SProductCreate, SProductUpdate


class IProductsRepository(Protocol):

    async def add_product(self, product: SProductCreate) -> ProductItem:
        ...

    async def update_product(self, product_id: int, data: SProductUpdate) -> ProductItem | None:
        ...

    async def delete_product(self, product_id: int) -> ProductItem | None:
        ...

    async def get_all_products(self, pagination: Pagination) -> list[ProductItem]:
        ...

    async def count_products(self) -> int:
        ...

    async def get_product_by_id(self, product_id: int) -> ProductItem | None:
        ...

    async def get_products_by_ids(self, product_ids: list[int]) -> list[ProductItem]:
        ...

    async def get_stock_by_ids(self, product_ids: list[int]) -> dict:
        ...

    async def decrease_stock(self, product_id: int, quantity: int) -> None:
        ...

    async def increase_stock(self, product_id: int, quantity: int) -> None:
        ...

