from app.domain.entities.categories import CategoryItem
from app.models.categories import Categories


class CategoryMapper:
    @staticmethod
    def to_entity(orm_model: Categories) -> CategoryItem:
        """Преобразует ORM модель в domain entity."""
        return CategoryItem(
            id=orm_model.id,
            name=orm_model.name,
            description=orm_model.description
        )
    
    @staticmethod
    def to_orm(entity: CategoryItem) -> dict[str, str]:
        """Преобразует entity в данные для ORM."""
        data = {
            "name": entity.name,
            "description": entity.description
        }
        if entity.id:
            data["id"] = entity.id
        return data


