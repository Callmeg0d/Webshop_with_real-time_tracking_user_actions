from app.domain.entities.product import ProductItem
from app.models.products import Products


class ProductMapper:
    @staticmethod
    def to_entity(orm: Products) -> ProductItem:
        """Преобразует ORM модель в domain entity."""
        return ProductItem(
            product_id=orm.product_id,
            name=orm.name,
            description=orm.description,
            price=orm.price,
            product_quantity=orm.product_quantity,
            image=orm.image,
            features=orm.features,
            category_id=orm.category_id,
        )

    @staticmethod
    def to_orm(entity: ProductItem) -> dict[str, str|int]:
        """Преобразует entity в данные для ORM."""
        data = {
            "name": entity.name,
            "description": entity.description,
            "price": entity.price,
            "product_quantity": entity.product_quantity,
            "image": entity.image,
            "features": entity.features,
            "category_id": entity.category_id,
        }

        return data

