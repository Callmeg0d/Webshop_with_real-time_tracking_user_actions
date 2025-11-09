from app.domain.entities.users import UserItem
from app.models import Users


class UserMapper:
    @staticmethod
    def to_entity(orm: Users) -> UserItem:
        """Преобразует ORM модель в domain entity."""
        return UserItem(
            id=orm.id,
            email = orm.email,
            hashed_password=orm.hashed_password,
            delivery_address=orm.delivery_address,
            name=orm.name,
            balance=orm.balance,
        )

    @staticmethod
    def to_orm(entity: UserItem) -> dict:
        """Преобразует entity в данные для ORM."""
        return {
            "email": entity.email,
            "hashed_password": entity.hashed_password,
            "delivery_address": entity.delivery_address,
            "name": entity.name,
            "balance": entity.balance,
        }