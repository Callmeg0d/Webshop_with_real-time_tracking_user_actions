from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.categories import CategoryItem
from app.repositories import CategoriesRepository


class CategoryService:
    def __init__(self,
                 db: AsyncSession,
                 category_repository: CategoriesRepository
    ):
        self.db = db
        self.category_repository = category_repository

    async def get_all_categories(self) -> List[CategoryItem]:
        """Получить все категории."""
        return await self.category_repository.get_all()

    async def get_category_by_id(self, category_id: int) -> Optional[CategoryItem]:
        """Получить категорию по ID."""
        return await self.category_repository.get_by_id(category_id)

    async def get_category_by_name(self, category_name: str) -> Optional[CategoryItem]:
        """Получить категорию по названию."""
        return await self.category_repository.get_by_name(category_name)

    async def create_category(self, category: CategoryItem) -> CategoryItem:
        """Создать новую категорию."""
        created = await self.category_repository.create(category)
        await self.db.commit()
        return created