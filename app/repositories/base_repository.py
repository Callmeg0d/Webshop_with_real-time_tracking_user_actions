from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий для выполнения общих операций с базой данных.

    Этот класс предоставляет базовые CRUD операции, которые могут быть унаследованы
    репозиториями моделей. Использует асинхронную сессию SQLAlchemy
    для взаимодействия с базой данных.

    ModelType: Класс модели SQLAlchemy, привязанный к Base
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Инициализация репозитория с моделью и сессией базы данных.

        Args:
            model: Класс модели SQLAlchemy
            db: Асинхронная сессия базы данных для выполнения запросов
        """
        self.model = model
        self.db = db

    async def get(self, id: int) -> Optional[ModelType]:
        """
        Получить один объект по его ID.

        Args:
            id: ID объекта для получения

        Returns:
            Экземпляр модели если найден, иначе None
        """
        result = await self.db.execute(select(self.model).where(self.model.id == id))  # type: ignore[attr-defined]
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Получить все объекты с поддержкой пагинации.

        Args:
            skip: Количество записей для пропуска (для пагинации)
            limit: Максимальное количество возвращаемых записей

        Returns:
            Список экземпляров моделей
        """
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, obj_in: dict) -> ModelType:
        """
        Создать новый объект в базе данных.

        Args:
            obj_in: Словарь со значениями полей для нового объекта

        Returns:
            Новый экземпляр модели
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """
        Обновить существующий объект новыми значениями.

        Args:
            db_obj: Существующий экземпляр модели для обновления
            obj_in: Словарь с парами поле-значение для обновления

        Returns:
            Обновленный экземпляр модели
        """
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        """
       Удалить объект по его ID.

       Args:
           id: ID объекта для удаления

       Returns:
           True если объект был удален, False если объект не найден
       """
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False
