from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.interfaces.products_repo import IProductsRepository
from app.schemas.products import SProducts
from app.exceptions import CannotFindProductWithThisId


class ProductService:
    def __init__(
            self,
            products_repository: IProductsRepository,
            db: AsyncSession
    ):
        self.products_repository = products_repository
        self.db = db

    async def get_all_products(self) -> list[SProducts]:
        products = await self.products_repository.get_all_products()
        return [SProducts.model_validate(p) for p in products]

    async def get_product_by_id(self, product_id: int) -> SProducts:
        product = await self.products_repository.get_product_by_id(product_id)

        if not product:
            raise CannotFindProductWithThisId

        return SProducts.model_validate(product)

    async def get_stock_by_ids(self, product_ids: list[int]) -> dict[int, int]:
        """Получает остатки товаров по списку ID"""
        return await self.products_repository.get_stock_by_ids(product_ids)

    async def decrease_stock(self, product_id: int, quantity: int) -> None:
        """Уменьшает остаток товара"""
        async with UnitOfWork(self.db):
            await self.products_repository.decrease_stock(product_id, quantity)

    async def increase_stock(self, product_id: int, quantity: int) -> None:
        """Увеличивает остаток товара (компенсация)"""
        async with UnitOfWork(self.db):
            await self.products_repository.increase_stock(product_id, quantity)

