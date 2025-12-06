from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import ProductsRepository
from app.schemas.products import SProducts
from app.exceptions import CannotFindProductWithThisId

class ProductService:
    def __init__(
            self,
            products_repository: ProductsRepository,
            db: AsyncSession
    ):
        self.products_repository = products_repository
        self.db = db

    async def get_all_products(self) -> List[SProducts]:
        products = await self.products_repository.get_all_products()
        return [SProducts.model_validate(p) for p in products]

    async def get_product_by_id(self, product_id: int) -> SProducts:
        product = await self.products_repository.get_product_by_id(product_id)

        if not product:
            raise CannotFindProductWithThisId

        return SProducts.model_validate(product)