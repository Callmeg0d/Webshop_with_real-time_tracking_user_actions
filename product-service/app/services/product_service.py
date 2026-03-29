from shared import get_logger

from app.domain.entities.product import ProductItem
from app.domain.interfaces.products_repo import IProductsRepository
from app.domain.interfaces.unit_of_work import IUnitOfWorkFactory
from app.schemas.products import Pagination, SProducts, SProductCreate, SProductUpdate
from app.exceptions import CannotFindProductWithThisId
from app.messaging.publisher import (
    publish_product_added,
    publish_product_removed,
    publish_product_updated,
)

logger = get_logger(__name__)


class ProductService:
    def __init__(
            self,
            products_repository: IProductsRepository,
            uow_factory: IUnitOfWorkFactory,
    ) -> None:
        self.products_repository: IProductsRepository = products_repository
        self.uow_factory: IUnitOfWorkFactory = uow_factory

    async def get_all_products(self, pagination: Pagination) -> list[SProducts]:
        logger.debug("Fetching all products")
        try:
            products = await self.products_repository.get_all_products(pagination)
            logger.debug(f"Found {len(products)} products")
            return [SProducts.model_validate(p) for p in products]
        except Exception as e:
            logger.error(f"Error fetching all products: {e}", exc_info=True)
            raise

    async def count_products(self) -> int:
        try:
            return await self.products_repository.count_products()
        except Exception as e:
            logger.error(f"Error counting products: {e}", exc_info=True)
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

    async def get_products_by_ids(self, product_ids: list[int]) -> list[SProducts]:
        """Получает товары по списку ID (для рекомендаций по просмотренным)"""
        if not product_ids:
            return []
        try:
            products = await self.products_repository.get_products_by_ids(product_ids)
            return [SProducts.model_validate(p) for p in products]
        except Exception as e:
            logger.error(f"Error fetching products by ids: {e}", exc_info=True)
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
            async with self.uow_factory.create():
                await self.products_repository.decrease_stock(product_id, quantity)
            logger.info(f"Stock decreased successfully for product {product_id}")
        except Exception as e:
            logger.error(f"Error decreasing stock for product {product_id}: {e}", exc_info=True)
            raise

    async def increase_stock(self, product_id: int, quantity: int) -> None:
        """Увеличивает остаток товара (компенсация)"""
        logger.info(f"Increasing stock for product {product_id} by {quantity} (compensation)")
        try:
            async with self.uow_factory.create():
                await self.products_repository.increase_stock(product_id, quantity)
            logger.info(f"Stock increased successfully for product {product_id}")
        except Exception as e:
            logger.error(f"Error increasing stock for product {product_id}: {e}", exc_info=True)
            raise

    async def add_product(self, product: SProductCreate) -> SProducts:
        logger.debug(f"Adding product {product.name}")
        try:
            async with self.uow_factory.create():
                created = await self.products_repository.add_product(product)
            if created:
                await publish_product_added(created)
            logger.info(f"Added product {product.name} successfully")
            return SProducts.model_validate(created)
        except Exception as e:
            logger.error(f"Error adding product {product.name}: {e}", exc_info=True)
            raise

    async def update_product(self, product_id: int, data: SProductUpdate) -> SProducts:
        logger.debug(f"Updating product {product_id}")
        try:
            async with self.uow_factory.create():
                updated = await self.products_repository.update_product(product_id, data)
            if not updated:
                raise CannotFindProductWithThisId
            await publish_product_updated(updated)
            logger.info(f"Updated product {product_id} successfully")
            return SProducts.model_validate(updated)
        except CannotFindProductWithThisId:
            raise
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}", exc_info=True)
            raise

    async def delete_product(self, product_id: int) -> None:
        logger.debug(f"Deleting product {product_id}")
        try:
            async with self.uow_factory.create():
                deleted = await self.products_repository.delete_product(product_id)
            if not deleted:
                raise CannotFindProductWithThisId
            await publish_product_removed(deleted)
            logger.info(f"Deleted product {product_id} successfully")
        except CannotFindProductWithThisId:
            raise
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}", exc_info=True)
            raise