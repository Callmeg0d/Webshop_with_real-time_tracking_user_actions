from typing import Protocol

from app.domain.entities.categories import CategoryItem


class ICategoriesRepository(Protocol):
    async def get_all(self) -> list[CategoryItem]:
        ...

    async def get_by_id(self, category_id: int) -> CategoryItem | None:
        ...

    async def get_by_name(self, name: str) -> CategoryItem | None:
        ...

    async def create(self, category: CategoryItem) -> CategoryItem:
        ...


