from typing import Protocol, List, Optional

from app.domain.entities.product import ProductItem


class IProductsRepository(Protocol):

    async def get_all_products(self) -> List[ProductItem]:
        ...

    async def get_product_by_id(self, product_id: int) -> Optional[ProductItem]:
        ...

    async def get_stock_by_ids(self, product_ids: List[int]) -> dict:
        ...

    async def decrease_stock(self, product_id: int, quantity: int) -> None:
        ...