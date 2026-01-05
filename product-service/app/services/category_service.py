from sqlalchemy.ext.asyncio import AsyncSession
from shared import get_logger

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.categories import CategoryItem
from app.domain.interfaces.categories_repo import ICategoriesRepository

logger = get_logger(__name__)


class CategoryService:
    def __init__(
        self,
        db: AsyncSession,
        category_repository: ICategoriesRepository
    ):
        self.db = db
        self.category_repository = category_repository

    async def get_all_categories(self) -> list[CategoryItem]:
        """Получить все категории."""
        logger.debug("Fetching all categories")
        try:
            categories = await self.category_repository.get_all()
            logger.debug(f"Found {len(categories)} categories")
            return categories
        except Exception as e:
            logger.error(f"Error fetching all categories: {e}", exc_info=True)
            raise

    async def get_category_by_id(self, category_id: int) -> CategoryItem | None:
        """Получить категорию по ID."""
        logger.debug(f"Fetching category {category_id}")
        try:
            category = await self.category_repository.get_by_id(category_id)
            if category:
                logger.debug(f"Category {category_id} found")
            else:
                logger.debug(f"Category {category_id} not found")
            return category
        except Exception as e:
            logger.error(f"Error fetching category {category_id}: {e}", exc_info=True)
            raise

    async def get_category_by_name(self, category_name: str) -> CategoryItem | None:
        """Получить категорию по названию."""
        logger.debug(f"Fetching category by name: {category_name}")
        try:
            category = await self.category_repository.get_by_name(category_name)
            if category:
                logger.debug(f"Category '{category_name}' found")
            else:
                logger.debug(f"Category '{category_name}' not found")
            return category
        except Exception as e:
            logger.error(f"Error fetching category by name '{category_name}': {e}", exc_info=True)
            raise

    async def create_category(self, category: CategoryItem) -> CategoryItem:
        """Создать новую категорию."""
        logger.info(f"Creating category: {category.name}")
        try:
            async with UnitOfWork(self.db):
                created = await self.category_repository.create(category)
            logger.info(f"Category created successfully: {created.name}")
            return created
        except Exception as e:
            logger.error(f"Error creating category '{category.name}': {e}", exc_info=True)
            raise


