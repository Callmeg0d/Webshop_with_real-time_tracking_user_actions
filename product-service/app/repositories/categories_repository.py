from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Categories
from app.domain.entities.categories import CategoryItem
from app.domain.mappers.category import CategoryMapper


class CategoriesRepository:
    """
    Репозиторий для работы с категориями товаров.

    Работает с domain entities (CategoryItem), используя маппер для преобразования
    между entities и ORM моделями.
    """

    def __init__(self, db: AsyncSession):
        """
        Инициализация репозитория категорий.

        Args:
            db: Асинхронная сессия базы данных
        """
        self.db = db
        self.mapper = CategoryMapper()

    async def get_all(self) -> list[CategoryItem]:
        """
        Получает все категории.

        Returns:
            Список domain entities категорий
        """
        result = await self.db.execute(select(Categories))
        orm_models = list(result.scalars().all())
        
        return [
            self.mapper.to_entity(orm_model)
            for orm_model in orm_models
            if orm_model is not None
        ]

    async def get_by_id(self, category_id: int) -> CategoryItem | None:
        """
        Получает категорию по ID.

        Args:
            category_id: ID категории

        Returns:
            Domain entity категории если найдена, иначе None
        """
        result = await self.db.execute(
            select(Categories).where(Categories.id == category_id)
        )
        orm_model = result.scalar_one_or_none()
        
        if not orm_model:
            return None
        
        return self.mapper.to_entity(orm_model)

    async def get_by_name(self, name: str) -> CategoryItem | None:
        """
        Получает категорию по названию.

        Args:
            name: Название категории

        Returns:
            Domain entity категории если найдена, иначе None
        """
        result = await self.db.execute(
            select(Categories).where(Categories.name == name)
        )
        orm_model = result.scalar_one_or_none()
        
        if not orm_model:
            return None
        
        return self.mapper.to_entity(orm_model)

    async def create(self, category: CategoryItem) -> CategoryItem:
        """
        Создает новую категорию.

        Args:
            category: Domain entity категории для создания

        Returns:
            Созданная domain entity категории с ID из БД
        """
        orm_data = self.mapper.to_orm(category)
        orm_model = Categories(**orm_data)
        self.db.add(orm_model)
        await self.db.flush()
        
        return self.mapper.to_entity(orm_model)


