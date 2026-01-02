from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.domain.entities.categories import CategoryItem
from app.domain.interfaces.categories_repo import ICategoriesRepository


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
        return await self.category_repository.get_all()

    async def get_category_by_id(self, category_id: int) -> CategoryItem | None:
        """Получить категорию по ID."""
        return await self.category_repository.get_by_id(category_id)

    async def get_category_by_name(self, category_name: str) -> CategoryItem | None:
        """Получить категорию по названию."""
        return await self.category_repository.get_by_name(category_name)

    async def create_category(self, category: CategoryItem) -> CategoryItem:
        """Создать новую категорию."""
        async with UnitOfWork(self.db):
            created = await self.category_repository.create(category)
        return created


