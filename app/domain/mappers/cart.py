from app.domain.entities.cart import CartItem
from app.models import ShoppingCarts

class CartMapper:
    @staticmethod
    def to_entity(orm_model: ShoppingCarts) -> CartItem:
        """Преобразует ORM модель в domain entity."""
        return CartItem(
            cart_id=orm_model.cart_id,
            user_id=orm_model.user_id,
            product_id=orm_model.product_id,
            quantity=orm_model.quantity,
            total_cost=orm_model.total_cost
        )

    @staticmethod
    def to_orm(entity: CartItem) -> dict:
        """Преобразует entity в данные для ORM."""
        return {
            # cart_id не включаем - БД сама присвоит при создании
            "user_id": entity.user_id,
            "product_id": entity.product_id,
            "quantity": entity.quantity,
            "total_cost": entity.total_cost
        }