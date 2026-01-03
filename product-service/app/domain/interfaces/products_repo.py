from typing import Protocol

from app.domain.entities.product import ProductItem


class IProductsRepository(Protocol):

    async def get_all_products(self) -> list[ProductItem]:
        ...

    async def get_product_by_id(self, product_id: int) -> ProductItem | None:
        ...

    async def get_stock_by_ids(self, product_ids: list[int]) -> dict:
        ...

    async def decrease_stock(self, product_id: int, quantity: int) -> None:
        ...

    async def increase_stock(self, product_id: int, quantity: int) -> None:
        ...

