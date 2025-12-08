from typing import Protocol, List, Optional

from app.domain.entities.categories import CategoryItem


class ICategoriesRepository(Protocol):
    async def get_all(self) -> List[CategoryItem]:
        ...

    async def get_by_id(self, category_id: int) -> Optional[CategoryItem]:
        ...

    async def get_by_name(self, name: str) -> Optional[CategoryItem]:
        ...

    async def create(self, category: CategoryItem) -> CategoryItem:
        ...

