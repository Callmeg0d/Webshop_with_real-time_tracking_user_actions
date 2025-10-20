"""
Скрипт для загрузки seed данных в базу данных.
Использование: poetry run python load_seed_data.py
"""
import asyncio
from typing import Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from app.config import settings
from app.models.categories import Categories
from app.models.products import Products
from app.models.users import Users
from app.models.reviews import Reviews
from app.seed_data import CATEGORIES, PRODUCTS, USERS, REVIEWS


async def clear_database(session: AsyncSession) -> None:
    # Удаляем в правильном порядке (с учётом foreign keys)
    await session.execute(text("DELETE FROM reviews;"))
    await session.execute(text("DELETE FROM shopping_carts;"))
    await session.execute(text("DELETE FROM orders;"))
    await session.execute(text("DELETE FROM products;"))
    await session.execute(text("DELETE FROM categories;"))
    await session.execute(text("DELETE FROM users;"))
    
    # Сброс sequence для ID
    await session.execute(text("ALTER SEQUENCE categories_id_seq RESTART WITH 1;"))
    await session.execute(text("ALTER SEQUENCE products_product_id_seq RESTART WITH 1;"))
    await session.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1;"))
    await session.execute(text("ALTER SEQUENCE reviews_review_id_seq RESTART WITH 1;"))
    
    await session.commit()
    print("[OK] База данных очищена")


async def load_categories(session: AsyncSession) -> dict[str, int]:
    """Загружает категории и возвращает маппинг имя -> id."""
    print(f"[LOAD] Загрузка категорий ({len(CATEGORIES)})...")
    
    category_map = {}
    for cat_data in CATEGORIES:
        category = Categories(
            name=cat_data["name"],
            description=cat_data.get("description")
        )
        session.add(category)
        await session.flush()  # Получаем ID
        category_map[cat_data["name"]] = category.id
        print(f"  + {cat_data['name']}")
    
    await session.commit()
    print(f"[OK] Загружено {len(CATEGORIES)} категорий")
    return category_map


async def load_products(session: AsyncSession, category_map: dict[str, int]) -> dict[str, int]:
    """Загружает продукты и возвращает маппинг имя -> id."""
    print(f"[LOAD] Загрузка продуктов ({len(PRODUCTS)})...")
    
    product_map: dict[str, int] = {}
    for prod_data in PRODUCTS:
        # Получаем category_id по имени категории
        category_name = str(prod_data.get("category_name", ""))
        category_id = category_map.get(category_name)
        if not category_id:
            print(f"  [WARN] Категория '{category_name}' не найдена для продукта '{prod_data['name']}'")
            continue
        
        product = Products(
            name=str(prod_data["name"]),
            description=str(prod_data["description"]),
            price=int(prod_data["price"]),  # type: ignore[call-overload]
            product_quantity=int(prod_data["product_quantity"]),  # type: ignore[call-overload]
            image=prod_data.get("image"),  # type: ignore[arg-type]
            features=prod_data.get("features"),  # type: ignore[arg-type]
            category_id=category_id
        )
        session.add(product)
        await session.flush()  # Получаем ID
        product_map[str(prod_data["name"])] = product.product_id
        print(f"  + {prod_data['name']} ({category_name})")
    
    await session.commit()
    print(f"[OK] Загружено {len(product_map)} продуктов")
    return product_map


async def load_users(session: AsyncSession) -> dict[str, int]:
    """Загружает пользователей и возвращает маппинг email -> id."""
    print(f"[LOAD] Загрузка пользователей ({len(USERS)})...")
    
    user_map = {}
    for user_data in USERS:
        user = Users(
            email=user_data["email"],
            name=user_data.get("name"),
            hashed_password=user_data["hashed_password"],
            delivery_address=user_data.get("delivery_address")
        )
        session.add(user)
        await session.flush()  # Получаем ID
        user_map[user_data["email"]] = user.id
        print(f"  + {user_data['email']} ({user_data.get('name', 'Без имени')})")
    
    await session.commit()
    print(f"[OK] Загружено {len(USERS)} пользователей")
    print("[INFO] Пароль для всех пользователей: password123")
    return user_map


async def load_reviews(
    session: AsyncSession,
    user_map: dict[str, int],
    product_map: dict[str, int]
) -> None:
    """Загружает отзывы."""
    print(f"[LOAD] Загрузка отзывов ({len(REVIEWS)})...")
    
    loaded_count = 0
    for review_data in REVIEWS:
        user_email = str(review_data.get("user_email", ""))
        product_name = str(review_data.get("product_name", ""))
        
        user_id = user_map.get(user_email)
        product_id = product_map.get(product_name)
        
        if not user_id:
            print(f"  [WARN] Пользователь '{user_email}' не найден")
            continue
        
        if not product_id:
            print(f"  [WARN] Продукт '{product_name}' не найден")
            continue
        
        review = Reviews(
            user_id=user_id,
            product_id=product_id,
            rating=int(review_data["rating"]),  # type: ignore[call-overload]
            feedback=str(review_data["feedback"])
        )
        session.add(review)
        loaded_count += 1
        print(f"  + {product_name} - {review_data['rating']} звезд от {user_email}")
    
    await session.commit()
    print(f"[OK] Загружено {loaded_count} отзывов")


async def main() -> None:
    """Основная функция для загрузки всех seed данных."""
    print("=" * 60)
    print("[START] Начало загрузки seed данных")
    print("=" * 60)
    
    # Создаём engine и session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        try:
            # Очищаем базу данных
            await clear_database(session)
            
            # Загружаем данные в правильном порядке
            category_map = await load_categories(session)
            product_map = await load_products(session, category_map)
            user_map = await load_users(session)
            await load_reviews(session, user_map, product_map)

        except Exception as e:
            print(f"\n[ERROR] Ошибка при загрузке данных: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

