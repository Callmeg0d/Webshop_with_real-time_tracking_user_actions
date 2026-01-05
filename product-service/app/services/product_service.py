from sqlalchemy.ext.asyncio import AsyncSession
from shared import get_logger

from app.core.unit_of_work import UnitOfWork
from app.domain.interfaces.products_repo import IProductsRepository
from app.schemas.products import SProducts
from app.exceptions import CannotFindProductWithThisId

logger = get_logger(__name__)


class ProductService:
    def __init__(
            self,
            products_repository: IProductsRepository,
            db: AsyncSession
    ):
        self.products_repository = products_repository
        self.db = db

    async def get_all_products(self) -> list[SProducts]:
        logger.debug("Fetching all products")
        try:
            products = await self.products_repository.get_all_products()
            logger.debug(f"Found {len(products)} products")
            return [SProducts.model_validate(p) for p in products]
        except Exception as e:
            logger.error(f"Error fetching all products: {e}", exc_info=True)
            raise

    async def get_product_by_id(self, product_id: int) -> SProducts:
        logger.debug(f"Fetching product {product_id}")
        try:
            product = await self.products_repository.get_product_by_id(product_id)

            if not product:
                logger.warning(f"Product {product_id} not found")
                raise CannotFindProductWithThisId

            logger.debug(f"Product {product_id} retrieved successfully")
            return SProducts.model_validate(product)
        except CannotFindProductWithThisId:
            raise
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}", exc_info=True)
            raise

    async def get_stock_by_ids(self, product_ids: list[int]) -> dict[int, int]:
        """Получает остатки товаров по списку ID"""
        logger.debug(f"Fetching stock for {len(product_ids)} products")
        try:
            stock = await self.products_repository.get_stock_by_ids(product_ids)
            logger.debug(f"Stock retrieved for {len(stock)} products")
            return stock
        except Exception as e:
            logger.error(f"Error fetching stock for products: {e}", exc_info=True)
            raise

    async def decrease_stock(self, product_id: int, quantity: int) -> None:
        """Уменьшает остаток товара"""
        logger.info(f"Decreasing stock for product {product_id} by {quantity}")
        try:
            async with UnitOfWork(self.db):
                await self.products_repository.decrease_stock(product_id, quantity)
            logger.info(f"Stock decreased successfully for product {product_id}")
        except Exception as e:
            logger.error(f"Error decreasing stock for product {product_id}: {e}", exc_info=True)
            raise

    async def increase_stock(self, product_id: int, quantity: int) -> None:
        """Увеличивает остаток товара (компенсация)"""
        logger.info(f"Increasing stock for product {product_id} by {quantity} (compensation)")
        try:
            async with UnitOfWork(self.db):
                await self.products_repository.increase_stock(product_id, quantity)
            logger.info(f"Stock increased successfully for product {product_id}")
        except Exception as e:
            logger.error(f"Error increasing stock for product {product_id}: {e}", exc_info=True)
            raise

